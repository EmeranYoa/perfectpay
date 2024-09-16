# USSD Service - PerfectPay API

## Description

Ce projet est une implémentation d'un service USSD basé sur FastAPI pour gérer les opérations telles que l'inscription, le transfert d'argent, la consultation de solde, le paiement de services, la recharge de compte, et bien plus. L'API respecte les mêmes flux que ceux implémentés dans le script PHP fourni.

### Fonctionnalités

- Inscription d'utilisateurs via USSD.
- Transfert d'argent entre clients.
- Consultation de solde.
- Retrait de solde via des marchands.
- Paiement de services.
- Recharge de solde.
- Sauvegarde des sessions et des états de l'utilisateur dans une base de données SQL (via SQLAlchemy).

## Technologies Utilisées

- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework web rapide et moderne pour Python.
- **SQLAlchemy** - ORM pour la gestion de la base de données.
- **MySQL / PostgreSQL / SQLite** - Base de données relationnelle (choisissez celle que vous souhaitez utiliser).
- **Docker** (optionnel) - Pour containeriser l'application.
- **Pydantic** - Pour la validation des schémas de requêtes et réponses.

## Prérequis

- Python 3.9+
- Un gestionnaire de base de données relationnelle compatible avec SQLAlchemy (MySQL)
- [pip](https://pip.pypa.io/en/stable/) - Gestionnaire de paquets Python.

## Installation

1. Clonez ce repository sur votre machine locale :

   ```bash
   git clone https://github.com/EmeranYoa/perfectpay.git
   cd perfectpay
   ```

2. Créez un environnement virtuel et activez-le :

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

3. Installez les dépendances requises :

   ```bash
   pip install -r requirements.txt
   ```

4. Créé un fichier `.env` à partir du fichier `.env.example` qui se trouve dans app et configurez-le avec vos informations d'identification de base de données et d'autres paramètres.

## Utilisation

1. Démarrez le serveur FastAPI :

   ```bash
   uvicorn main:app --reload
   ```

   Cela démarre le serveur en mode développement à l'adresse [http://127.0.0.1:8000](http://127.0.0.1:8000).

2. Testez l'API via Swagger en visitant :

   ```
   http://127.0.0.1:8000/v1/docs
   ```

3. Envoyez des requêtes à l'API :

   Par exemple, pour tester un point de terminaison USSD, vous pouvez envoyer une requête POST à `/ussd/` avec un payload JSON comme celui-ci :

   ```json
   {
     "sessionid": "1234567890",
     "msisdn": "#237*100#",
     "message": "1"
   }
   ```

   La réponse pourrait ressembler à :

   ```json
   {
     "message": "Entrez le numéro du bénéficiaire",
     "command": "CON"
   }
   ```

## Structure du projet

```bash
.
├── app
│   ├── __init__.py
│   ├── main.py                # Point d'entrée principal pour FastAPI
│   ├── models                 #  dossier pour les modèles SQLAlchemy
│   ├── routes                 # Définition des routes pour les différentes opérations
│   ├── core                   # Dossier pour les fonctions metiers
│   ├── schemas                # Schémas Pydantic pour valider les requêtes et réponses
│   ├── config                 # Dossier de configuration (URL de la base de données, etc.)
│   ├── .env                   # Fichier d'environnement
├── alembic                    # Dossier Alembic pour la gestion des migrations
├── Dockerfile                 # Fichier Docker (optionnel)
├── requirements.txt           # Fichier listant les dépendances du projet
├── README.md                  # Documentation du projet (ce fichier)
```

## Alimbic

Alembic est utilisé pour la gestion des migrations de la base de données. Pour créer une nouvelle migration, exécutez :

```bash
alembic revision --autogenerate -m "Nom de la migration"
```

Pour appliquer les migrations :

```bash
alembic upgrade head
```

Pour revenir à une version spécifique :

```bash
alembic downgrade <version_id>
```

Pour visualiser l'état actuel de la base de données :

```bash
alembic current
```

<!-- ## Licence
Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails. -->
