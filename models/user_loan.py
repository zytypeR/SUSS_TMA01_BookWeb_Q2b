from mongoengine import Document, StringField, ReferenceField, DateTimeField, IntField, BooleanField
from datetime import datetime
from flask_login import UserMixin
from .books import Book 

class User(Document, UserMixin):
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    name = StringField(required=True)
    is_admin = BooleanField(default=False) 
    avatar_file = StringField(default='default-avatar.png')
    meta = {'collection': 'user'}
    
    @classmethod
    def getUser(cls, email):
        """Finds a user object by email for login/registration check."""
        return cls.objects(email=email).first()

    @classmethod
    def createUser(cls, email, password, name):
        """Creates and saves a new user."""
        new_user = cls(email=email, password=password, name=name)
        new_user.save()
        
    @classmethod
    def getUserById(cls, user_id):
        """Finds a user object by ID (used by Flask-Login)."""
        return cls.objects(id=user_id).first()

class Loan(Document):
    member = ReferenceField(User, required=True)
    book = ReferenceField(Book, required=True)
    
    borrowDate = DateTimeField(default=datetime.utcnow, required=True)
    returnDate = DateTimeField()
    
    renewCount = IntField(default=0)
    meta = {'collection': 'loan'}