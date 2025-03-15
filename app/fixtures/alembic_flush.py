import subprocess
from app.configs.database import Base, engine
from app.configs.config import settings

ALEMBIC_CONFIG = "alembic.ini"

def alembic_flush():
    """
    Flush the database using Alembic by downgrading and upgrading migrations.
    """
    _protect_production_environment()
    print("Flushing the database with Alembic...")
    try:
        # Downgrade to base (drop all tables)
        subprocess.run(
            ["alembic", "-c", ALEMBIC_CONFIG, "downgrade", "base"],
            check=True,
        )
        print("Downgraded to base (all tables dropped).")

        # Upgrade to head (recreate all tables)
        subprocess.run(
            ["alembic", "-c", ALEMBIC_CONFIG, "upgrade", "head"],
            check=True,
        )
        print("Upgraded to head (all tables recreated).")

    except subprocess.CalledProcessError as e:
        print(f"Error while flushing the database: {e}")
        raise RuntimeError("Database flush failed.")

def _protect_production_environment():
    """
    Prevent flush operation in production environments.
    """
    environment = settings.APP_ENV
    print(f"Current environment: {environment}")

    if environment == "production":
        raise RuntimeError("Cannot flush the database in production environment!")