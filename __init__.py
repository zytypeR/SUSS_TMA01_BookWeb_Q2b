from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager, UserMixin
from mongoengine import Document

# APPLICATION FACTORY

def create_app(): 
    """
    Initializes and configures the Flask application, MongoEngine, and Flask-Login.
    """
    app = Flask(__name__)
    
    # mongo setup configuration
    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    app.config['MONGODB_SETTINGS'] = {
        'db': 'SUSS_TMA01_BookWeb_Q2B', 
        'host': 'localhost',
        'port': 27017
    }
    app.static_folder = 'assets' 
    
    # initialize extensions
    db = MongoEngine(app)
    
    # flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please login or register first to get an account."
    
    return app, db, login_manager

app, db, login_manager = create_app()

# ensures all models are registered with MongoEngine.
from .models.books import Book
from .models.user_loan import User, Loan

@login_manager.user_loader
def load_user(user_id):
    return None 