# Content Platform

Plateforme de diffusion de contenu statique cloud-native, déployée sur Azure Kubernetes Service (AKS).

## Architecture

L'application est une API REST Flask qui lit des fichiers JSON/YAML depuis Azure Blob Storage et les expose à des clients web, mobile ou partenaires.
```
GitHub (code + CI/CD)
       |
       v
GHCR (image Docker)
       |
       v
AKS (Kubernetes)
  ├── Deployment (2 pods Flask)
  ├── Service (ClusterIP)
  ├── Ingress (NGINX)
  ├── ConfigMap (configuration)
  └── Secret (clé Blob Storage)
       |
       v
Azure Blob Storage (events.json, news.json, faq.yaml)
```

Le cache mémoire TTL (60s) évite de solliciter Blob Storage à chaque requête.

## Endpoints

| Endpoint | Méthode | Description |
|---|---|---|
| `/` | GET | Interface web |
| `/api/events` | GET | Liste des événements |
| `/api/news` | GET | Liste des actualités |
| `/api/faq` | GET | Foire aux questions |
| `/healthz` | GET | Vérification de vie |
| `/readyz` | GET | Vérification de disponibilité |

## Lancer l'application

### En local
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
python app/main.py
```

Ouvrir : http://localhost:5000

### Avec Docker
```bash
docker build -t content-platform .
docker run -p 5000:5000 content-platform
```

Ouvrir : http://localhost:5000

### Depuis AKS
```bash
kubectl port-forward service/content-platform 9090:80 -n content-platform
```

Ouvrir : http://localhost:9090

## Lancer les tests
```bash
pytest tests/ -v
```

## Variables d'environnement

| Variable | Description | Par défaut |
|---|---|---|
| `AZURE_STORAGE_CONNECTION_STRING` | Chaîne de connexion Blob Storage | Non défini (mode mock local) |
| `AZURE_CONTAINER_NAME` | Nom du conteneur Blob | `content` |

Si `AZURE_STORAGE_CONNECTION_STRING` n'est pas défini, l'app lit les fichiers dans `app/mock_data/`.

## Structure du projet
```
content-platform/
├── app/
│   ├── main.py          # Application Flask
│   ├── cache.py         # Cache mémoire TTL
│   └── mock_data/       # Données de test locales
├── tests/
│   └── test_endpoints.py
├── k8s/                 # Manifests Kubernetes
├── .github/workflows/   # Pipeline CI/CD
├── Dockerfile
└── requirements.txt
```

## CI/CD

Le pipeline GitHub Actions se déclenche à chaque push sur `main` :

1. Lint (flake8)
2. Tests (pytest)
3. Build de l'image Docker
4. Push sur GHCR
5. Déploiement sur AKS