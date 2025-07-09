"""
Database configuration and models
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def init_app(app):
    """Initialize database with app"""
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        # Import models to register them
        from . import models
        
        # Create tables
        db.create_all()
