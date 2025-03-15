import typer
from app.fixtures.seed import seed_database
from app.configs.database import SessionLocal
from app.fixtures.alembic_flush import  alembic_flush
from app.core.cybersource_create_webhook import create_wallet_webhook

app = typer.Typer()

@app.command()
def seed(flush: bool = typer.Option(False, help="Flush the database before seeding.")):
    """
    Seed the database with initial data.
    Optionally flush the database before seeding.
    """
    db = SessionLocal()
    try:
        if flush:
            alembic_flush()
        seed_database(db)
    finally:
        db.close()

@app.command()
def flush():
    """
    Flush the database.
    """
    alembic_flush()
    typer.echo("Database flushed successfully.")

@app.command()
def webhook(create: bool = typer.Option(True, help="create webhook or get")):
 if create:
   typer.echo("Creating webhook...")
   response = create_wallet_webhook()
   typer.echo("*"*100)
   typer.echo(response)
   typer.echo("*"*100)
   typer.echo("Webhook created successfully.")
   return

 typer.echo("*"*10 + "LIST OR GET WEBHOOK" + "*"*100)
if __name__ == "__main__":
    app()
