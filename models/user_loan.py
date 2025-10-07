from mongoengine import Document, StringField, ReferenceField, DateTimeField, IntField
from datetime import datetime
from .books import Book # CRITICAL: Import Book model for the ReferenceField

class User(Document):
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
    # ReferenceField links to the other document classes
    member = ReferenceField(User, required=True)
    book = ReferenceField(Book, required=True)
    
    borrowDate = DateTimeField(default=datetime.utcnow, required=True)
    returnDate = DateTimeField() # Nullable if not yet returned
    
    renewCount = IntField(default=0)
    meta = {'collection': 'loan'}
