from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from drive.forms import UploadFileForm
from django.http import FileResponse, Http404
from .models import Document, Folder
from django.db import models
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, LoginForm, DocumentForm, FolderForm
import os
from django.core.files.storage import default_storage
from django.conf import settings
import mimetypes
from collections import defaultdict
from django.http import HttpResponse
from io import BytesIO
import matplotlib.pyplot as plt


# Create your views here.

def login(request):
    # Si l'utilisateur est déjà connecté, on le redirige vers la page de téléchargement
    if request.user.is_authenticated:
        return redirect('upload')

    signup_form = SignupForm()
    login_form = LoginForm()

    # Gestion de l'inscription
    if request.method == 'POST' and 'signup' in request.POST:
        signup_form = SignupForm(request.POST)
        if signup_form.is_valid():
            user = signup_form.save(commit=False)
            user.set_password(signup_form.cleaned_data['password'])  # Hash du mot de passe
            user.save()
            auth_login(request, user)
            return redirect('upload')

    # Gestion de la connexion
    if request.method == 'POST' and 'login' in request.POST:
        login_form = LoginForm(request, data=request.POST)
        if login_form.is_valid():
            user = login_form.get_user()
            auth_login(request, user)
            return redirect('upload')

    return render(request, 'login.html', {'signup_form': signup_form, 'login_form': login_form})

def check_disk_space(user, file_size):
    total_size = Document.objects.filter(user=user).aggregate(models.Sum('size'))['size__sum'] or 0
    if total_size + file_size > 100 * 1024 * 1024:  # 100 Mo
        return False
    return True



@login_required
def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            user_file = form.save(commit=False)
            user_file.user = request.user
            #user_file.user = None
            file_size = user_file.file.size

            # Vérifier la limite d’espace disque
            if file_size > 40 * 1024 * 1024:  # 40 Mo
                messages.error(request, "La taille de fichier maximale autorisée est de 40 Mo.")
            elif not check_disk_space(request.user, file_size):
            #elif not check_disk_space(None, file_size):
                messages.error(request, "Espace disque dépassé !")
            else:
                user_file.save()  # Enregistrer le fichier
                return redirect('documents2')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


def custom_logout(request):
    auth_logout(request)
    return redirect('login')


@login_required
def list_documents2(request, folder_id=None):
    # Dossiers racine et documents hors dossiers
    folders = Folder.objects.filter(user=request.user, parent__isnull=True)
    documents = Document.objects.filter(user=request.user, folder__isnull=True)
    return render(request, 'list_documents2.html', {'documents': documents, 'folders': folders})


@login_required
def confirm_delete(request, document_id):
    document = get_object_or_404(Document, id=document_id, user=request.user)
    return render(request, 'confirm_delete.html', {'document': document})

@login_required
def delete_document(request, document_id):
    document = get_object_or_404(Document, id=document_id, user=request.user)
    if request.method == "POST":
        # Supprime d'abord le document de la base de données
        document.delete()

        # Ensuite, supprime le fichier s'il est toujours présent
        if document.file:
            try:
                document.file.delete(save=False)  # Supprime le fichier sans sauvegarder l'instance
            except Exception as e:
                print("Erreur lors de la suppression du fichier :", e)
        
        messages.success(request, "Document supprimé avec succès.")
        return redirect('documents2')

    return render(request, 'confirm_delete.html', {'document': document})

@login_required
def move_document(request, document_id):
    document = get_object_or_404(Document, id=document_id, user=request.user)
    
    if request.method == "POST":
        # Récupérer l'ID du dossier de destination
        new_folder_id = request.POST.get("new_path")
        
        # Retrouver le dossier cible
        new_folder = get_object_or_404(Folder, id=new_folder_id, user=request.user)
        
        # Définir le chemin source et le chemin cible pour le fichier
        old_path = document.file.path
        new_path = os.path.join(settings.MEDIA_ROOT, f'user_{request.user.id}', new_folder.get_folder_path(), os.path.basename(old_path))
        
        # Déplacer le fichier
        try:
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            os.rename(old_path, new_path)
        except Exception as e:
            messages.error(request, "Erreur lors du déplacement du fichier.")
            return redirect('documents2')
        
        # Mettre à jour le champ `file` et `folder` du document
        document.file.name = os.path.join(f'user_{request.user.id}', new_folder.get_folder_path(), os.path.basename(document.file.name))
        document.folder = new_folder
        document.save()  # Enregistrer les modifications dans la base de données
        
        messages.success(request, "Document déplacé avec succès.")
        return redirect('documents2')
    
    else:
        folders = Folder.objects.filter(user=request.user)
        return render(request, 'move_document.html', {'document': document, 'folders': folders})



@login_required
def rename_document(request, document_id):
    document = get_object_or_404(Document, id=document_id, user=request.user)
    if request.method == 'POST':
        new_name = request.POST.get('new_name')

        # Récupérer l'extension d'origine
        original_extension = os.path.splitext(document.file.name)[1]  # ex : ".jpg"

        # Si l'utilisateur n'a pas fourni l'extension, on ajoute celle d'origine
        if not os.path.splitext(new_name)[1]:
            new_name += original_extension

        old_path = document.file.path
        new_path = os.path.join(os.path.dirname(old_path), new_name)

        try:
            # Renommer le fichier dans le système de fichiers avec default_storage
            default_storage.rename(document.file.name, new_path)

            # Mettre à jour le chemin du fichier dans la base de données
            document.file.name = f'user/{request.user.id}/{new_name}'
            document.save(update_fields=['file'])

            messages.success(request, "Document renommé avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur lors du renommage : {e}")
        
        return redirect('documents2')
    
    return render(request, 'rename_document.html', {'document': document})


@login_required
def download_document(request, document_id):
    # Récupérer le document spécifié par l'ID et s'assurer que l'utilisateur est le propriétaire
    document = get_object_or_404(Document, id=document_id, user=request.user)
    
    # Vérifier que le fichier existe sur le système de fichiers
    file_path = document.file.path
    if not os.path.exists(file_path):
        raise Http404("Le fichier n'existe pas.")
    
    # Ouvrir le fichier et le renvoyer dans la réponse
    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=document.file.name)
    return response


@login_required
def create_folder(request):
    if request.method == 'POST':
        
        form = FolderForm(request.POST)
        print(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.user = request.user  # Associe le dossier à l'utilisateur actuel
            folder.parent = None  # Dossier racine, donc pas de parent
            folder.save()
            

            # Créer un répertoire physique pour ce dossier dans 'media'
            folder_path = os.path.join(settings.MEDIA_ROOT,  "user_"+str(folder.user.id), folder.name)
            os.makedirs(folder_path, exist_ok=True)  # Crée le dossier si nécessaire
            print(folder.id)
            

            return redirect('documents2')  # Redirige vers la liste des documents
        
    return redirect('documents2')  # Redirige vers la liste même si la requête n'est pas POST

@login_required
def open_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    folders = folder.folders.all()
    documents = folder.documents_in_folder.all()
    return render(request, 'open_folder.html', {'documents': documents, 'folders': folders})


@login_required
def delete_folder(request, folder_id: int):
    
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    if request.method == "POST":
        print(2)
        # Supprimer le dossier physique
        folder_path = os.path.join(settings.MEDIA_ROOT, "user_"+str(folder.user.id), folder.name)
        try:
            if os.path.exists(folder_path):
                
                os.rmdir(folder_path)  # Supprimer le dossier physique
        except Exception as e:
            print("Erreur lors de la suppression du dossier :", e)
        print(22)
        

        # Ensuite, supprimer les fichiers s'ils sont toujours présents
        for document in folder.documents.all():
            if document.file:
                try:
                    document.file.delete(save=False)  # Supprimer le fichier sans sauvegarder l'instance
                except Exception as e:
                    print("Erreur lors de la suppression du fichier :", e)

        # Supprimer d'abord le dossier de la base de données
        folder.delete()
        
        messages.success(request, "Dossier supprimé avec succès.")
        return redirect('documents2')

    return render(request, 'confirm_delete.html', {'document': folder})


@login_required
def stats(request):
    user_folder = os.path.join(settings.MEDIA_ROOT, f'user_{request.user.id}')
    document_types = defaultdict(int)

    # Analyse des types de documents
    for root, dirs, files in os.walk(user_folder):
        for file in files:
            file_path = os.path.join(root, file)
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type:
                if mime_type.startswith('image'):
                    document_types['Image'] += 1
                elif mime_type == 'application/pdf':
                    document_types['PDF'] += 1
                elif mime_type.startswith('video'):
                    document_types['Video'] += 1
                elif mime_type.startswith('audio'):
                    document_types['MP3'] += 1
                else:
                    document_types['Other'] += 1
            else:
                document_types['Other'] += 1

    # Création du graphique sans sauvegarder dans MEDIA
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(document_types.keys(), document_types.values(), color='skyblue')
    ax.set_xlabel('Document Type')
    ax.set_ylabel('Count')
    ax.set_title('Number of Documents by Type')
    plt.tight_layout()

    # Créer un buffer pour stocker l'image en mémoire
    from io import BytesIO
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)  # Revenir au début du buffer

    # Créer une réponse HTTP avec l'image en tant que contenu
    response = HttpResponse(buffer, content_type='image/png')
    response['Content-Disposition'] = 'inline; filename="user_stats.png"'

    # Fermer le graphique pour libérer la mémoire
    plt.close()

    # Retourner directement l'image dans la réponse HTTP
    return response

