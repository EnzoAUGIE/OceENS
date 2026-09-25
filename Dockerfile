FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && rm -rf /var/lib/apt/lists/*

# uv, version épinglée ; il utilise le Python de l'image (pas de téléchargement)
COPY --from=ghcr.io/astral-sh/uv:0.12.19 /uv /uvx /bin/
ENV UV_PYTHON_DOWNLOADS=never UV_LINK_MODE=copy UV_NO_CACHE=1

# Dépendances seules d'abord, depuis le lockfile : cette couche reste en cache
# tant que pyproject.toml et uv.lock ne changent pas
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-dev --no-install-project

# Le paquet oceens (code, templates, static, import) puis son installation.
# Installé en mode éditable depuis /app/src : la racine du projet reste /app,
# donc la base par défaut reste /app/database même si LOCAL_DATABASE_DIR est
# vide (le .env passé par docker compose l'écrase).
COPY ./src src
RUN uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"

# Le répertoire database/ est créé automatiquement par database.py au démarrage.
# Monter /app/database comme volume pour persister la base SQLite entre les redémarrages.
ENV LOCAL_DATABASE_DIR=/app/database
# Le fichier .env ne doit PAS être copié dans l'image : fournir les secrets via
# --env-file .env au lancement (docker run) ou via les variables d'environnement.

# Point d'entrée installé : uvicorn oceens.main:app sur 0.0.0.0:8000
CMD ["oceens"]
