from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager

# --- 1. APPLICATION FACTORY ---

def create_app(): 
    """
    Initializes and configures the Flask application, MongoEngine, and Flask-Login.
    """
    app = Flask(__name__)
    
    # --- Configuration ---
    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    app.config['MONGODB_SETTINGS'] = {
        # CRITICAL: Database name set to the requirement SUSS_TMA01_BookWeb_Q2B
        'db': 'SUSS_TMA01_BookWeb_Q2B', 
        'host': 'localhost',
        'port': 27017
    }
    app.static_folder = 'assets' 
    
    # --- Initialize Extensions ---
    db = MongoEngine(app)
    
    # Flask-Login setup (as per your previous example)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please login or register first to get an account."

    # Dummy current_user for templates
    class DummyUser:
        is_authenticated = False
    app.jinja_env.globals['current_user'] = DummyUser()
    
    return app, db, login_manager

# Execute the factory function immediately and make app, db, and login_manager globally accessible
app, db, login_manager = create_app()

# CRITICAL: Import the MongoEngine documents here AFTER db is initialized.
# This ensures all models (Book, User, Loan) are registered with MongoEngine.
from .models.books import Book
from .models.user_loan import User, Loan