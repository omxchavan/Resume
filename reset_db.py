from app import app, db

def reset_database():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("Dropped all database tables.")
        
        # Create all tables
        db.create_all()
        print("Created all database tables.")

if __name__ == "__main__":
    reset_database() 