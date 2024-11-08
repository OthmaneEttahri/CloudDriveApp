from django import forms
from .models import Document, Folder

from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm




class UploadFileForm(forms.ModelForm):
    class Meta : 
        model = Document
        fields = ('file',)

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Email / Nom d'utilisateur")
    password = forms.CharField(widget=forms.PasswordInput)

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file','folder']
    
class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'parent']

    