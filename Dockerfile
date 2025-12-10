FROM python:3.10-slim

# On se place dans /app dans le conteneur
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 1. Copie des requirements (qui sont dans le sous-dossier)
# On les copie à la racine de /app pour les installer
COPY ProjetDjango/requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copie du code source
# On prend le contenu du sous-dossier et on le met dans /app
COPY ProjetDjango/ .

# 3. Collectstatic
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Comme on a "aplati" la structure en copiant le contenu du sous-dossier vers /app,
# manage.py est maintenant directement dans /app.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "ProjetDjango.wsgi:application"]