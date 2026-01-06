import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def update_schema():
    app = create_app()
    with app.app_context():
        print("Checking database schema...")
        
        # Check if column exists
        inspector = db.inspect(db.engine)
        columns = [c['name'] for c in inspector.get_columns('user_path_progress')]
        
        if 'started_at' not in columns:
            print("Adding 'started_at' column to 'user_path_progress' table...")
            try:
                # Try PostgreSQL syntax first
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE user_path_progress ADD COLUMN started_at TIMESTAMP DEFAULT NOW() NOT NULL"))
                    conn.commit()
                print("Column added successfully (PostgreSQL syntax).")
            except Exception as e:
                print(f"PostgreSQL syntax failed: {e}")
                try:
                    # Try SQLite syntax
                    with db.engine.connect() as conn:
                        conn.execute(text("ALTER TABLE user_path_progress ADD COLUMN started_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL"))
                        conn.commit()
                    print("Column added successfully (SQLite syntax).")
                except Exception as e2:
                    print(f"SQLite syntax failed: {e2}")
                    print("Could not add column. Please check your database type.")
        else:
            print("'started_at' column already exists.")

if __name__ == "__main__":
    update_schema()
