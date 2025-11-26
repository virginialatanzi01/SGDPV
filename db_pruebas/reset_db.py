import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from data.database import Database

def reset_db():
    with app.app_context():
        Database.db.drop_all()
        Database.db.create_all()

if __name__ == '__main__':
    reset_db()