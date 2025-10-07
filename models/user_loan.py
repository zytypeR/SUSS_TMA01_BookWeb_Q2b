from mongoengine import Document, StringField, ReferenceField, DateTimeField, IntField
from datetime import datetime
from flask_login import UserMixin
from .books import Book 

class User(Document, UserMixin):
    """
    UML Class: User
    Fields: email, password, name
    """
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    name = StringField(required=True)
    meta = {'collection': 'user'}

class Loan(Document):
    """
    UML Class: Loan
    Fields: member, book, borrowDate, returnDate, renewCount
    """
    member = ReferenceField(User, required=True)
    book = ReferenceField(Book, required=True)
    
    borrowDate = DateTimeField(default=datetime.utcnow, required=True)
    returnDate = DateTimeField()
    
    renewCount = IntField(default=0)
    meta = {'collection': 'loan'}
