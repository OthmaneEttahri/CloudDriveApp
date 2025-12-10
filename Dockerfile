FROM python:3.10-slim

WORKDIR /app

# 1. Installation des dépendances système ET de SSH
# On installe openssh-server, on définit le mot de passe root à "Docker!" (standard Azure)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libpq-dev openssh-server \
    && echo "root:Docker!" | chpasswd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. Copie et installation des requirements
COPY ProjetDjango/requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copie du code source
COPY ProjetDjango/ .

# 4. Configuration SSH
COPY sshd_config /etc/ssh/
COPY entrypoint.sh .
# Rendre le script exécutable (très important)
RUN chmod +x entrypoint.sh

# 5. Collectstatic
RUN python manage.py collectstatic --noinput

# 6. Exposition des ports (8000 pour le Web, 2222 pour le SSH Azure)
EXPOSE 8000 2222

# 7. Lancement via le script
ENTRYPOINT ["./entrypoint.sh"]