"""
URL configuration for ProjetDjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from drive import views 
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from django.urls import re_path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("upload/", views.upload, name="upload"),
    path("login/", views.login, name="login"),
    path("logout/", views.custom_logout, name="logout"),
    path('delete_document/<int:document_id>/', views.delete_document, name='delete_document'),
    path('confirm_delete/<int:document_id>/', views.confirm_delete, name='confirm_delete'),
    path('move_document/<int:document_id>/', views.move_document, name='move_document'),
    path('rename_document/<int:document_id>/', views.rename_document, name='rename_document'),
    path('documents/<int:document_id>/download/', views.download_document, name='download_document'),
    path('list_documents2/', views.list_documents2, name='documents2'),
    path('create_folder/', views.create_folder, name='create_folder'),
    path('list_documents2/<int:folder_id>/', views.list_documents2, name='documents_in_folder'),
    path('open_folder/<int:folder_id>/', views.open_folder, name='open_folder'),
    path('delete_folder/<int:folder_id>/', views.delete_folder, name='delete_folder'),
    path('stats/', views.stats, name='stats'),



]