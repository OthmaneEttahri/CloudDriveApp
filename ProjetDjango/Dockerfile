# Image de base Python
FROM python:3.10-slim

# Éviter les fichiers .pyc et logs bufferisés
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dossier de travail dans le conteneur
WORKDIR /app

# Installation des dépendances système (nécessaire pour certaines libs)
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copie des requirements et installation
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copie du projet entier
COPY . /app/

# Collecte des fichiers statiques (CSS) pour WhiteNoise
RUN python manage.py collectstatic --noinput

# Exposition du port
EXPOSE 8000

# Commande de lancement (Gunicorn est mieux pour la prod)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "ProjetDjango.wsgi:application"]