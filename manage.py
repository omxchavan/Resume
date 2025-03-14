from flask.cli import FlaskGroup
from flask_migrate import init as init_db, migrate as migrate_db, upgrade as upgrade_db
from app import app, db

cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    """Create the database tables."""
    db.create_all()
    print("Created database tables.")

@cli.command("db_init")
def db_init():
    """Initialize migrations."""
    init_db(directory='migrations')
    print("Initialized migrations directory.")

@cli.command("db_migrate")
def db_migrate():
    """Create a new migration."""
    migrate_db(directory='migrations')
    print("Created new migration.")

@cli.command("db_upgrade")
def db_upgrade():
    """Apply migrations."""
    upgrade_db(directory='migrations')
    print("Applied migrations.")

if __name__ == "__main__":
    cli() 