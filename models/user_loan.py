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
        return cls.objects(email=email).first()

    @classmethod
    def createUser(cls, email, password, name):
        new_user = cls(email=email, password=password, name=name)
        new_user.save()
        
    @classmethod
    def getUserById(cls, user_id):
        return cls.objects(id=user_id).first()

class Loan(Document):
    member = ReferenceField(User, required=True)
    book = ReferenceField(Book, required=True)
    
    borrowDate = DateTimeField(default=datetime.utcnow, required=True)
    returnDate = DateTimeField()
    
    renewCount = IntField(default=0)
    meta = {'collection': 'loan'}

    @classmethod
    def getAllActiveLoansForUser(cls, user_id):
        return cls.objects(member=user_id, returnDate=None).all()
    
    @classmethod
    def getLoanById(cls, loan_id):
        from mongoengine.queryset import InvalidQueryError
        try:
            return cls.objects.get(id=loan_id)
        except InvalidQueryError:
            return None