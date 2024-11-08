from django.db import models
from django.contrib.auth.models import User 
import os 



def user_directory_path(instance, filename):
    # Créer un dossier par utilisateur dans 'media'
    return os.path.join(f'user_{instance.user.id}', filename)



class Document(models.Model):
    file = models.FileField(upload_to=user_directory_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    size = models.PositiveIntegerField(default=0)  # Taille du fichier en octets
    folder = models.ForeignKey('Folder', on_delete=models.CASCADE, related_name='documents_in_folder', null=True, blank=True)

    def save(self, *args, **kwargs):
        self.size = self.file.size  # Enregistrer la taille du fichier
        super().save(*args, **kwargs)

class Folder(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    documents = models.ManyToManyField(Document, blank=True,  related_name='contained_in_folders')
    folders = models.ManyToManyField('self', blank=True, related_name='contained_in_folders')

    def get_path(self):
        path = [self.name]
        folder = self
        while folder.parent is not None:
            folder = folder.parent
            path.insert(0, folder.name)
        return os.path.join(*path)

    def get_children(self):
        return list(self.folders.all()) + list(self.documents.all())

    def __str__(self):
        return self.name
    
    def get_folder_path(self):
        if self.parent:
            return f'{self.parent.get_folder_path()}/{self.name}'
        return self.name
