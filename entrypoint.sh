#!/bin/sh
set -e

# Démarrer le service SSH en arrière-plan
service ssh start

# Lancer l'application Django (Gunicorn)
exec gunicorn --bind 0.0.0.0:8000 ProjetDjango.wsgi:application