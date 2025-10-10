from mongoengine import Document, StringField, ReferenceField, DateTimeField, IntField, BooleanField
from datetime import datetime, timedelta
from flask_login import UserMixin
from .books import Book 
import random

def generate_valid_loan_date(start_dt):
    # calculate the target date (10-20 days from start_dt)
    random_days = random.randint(10, 20)
    calculated_date = start_dt.date() + timedelta(days=random_days)
    today_utc = datetime.utcnow().date()
    if calculated_date > today_utc:
        return today_utc
    else:
        return calculated_date

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
    def create_loan_document(cls, user_obj, book_obj):
        # check if user does not already have an unreturned loan for this book
        existing_loan = cls.objects(member=user_obj.id, book=book_obj.id, returnDate=None).first()
        if existing_loan:
            return False, f"You already have an active loan for '{book_obj.title}'."

        if book_obj.borrow(): 
            # generate a random number of days between 10 and 20
            past_days = random.randint(10, 20)
            borrow_date_past = datetime.utcnow() - timedelta(days=past_days)
            new_loan = cls(
                member=user_obj, 
                book=book_obj, 
                borrowDate=borrow_date_past
            )
            new_loan.save()
            return True, f"Successfully borrowed '{book_obj.title}'. Enjoy reading!"
        else:
            return False, f"Oops, '{book_obj.title}' is currently out of copies."
        
    @classmethod
    def get_all_loans_for_user(cls, user_obj):
        return cls.objects(member=user_obj.id).order_by('-borrowDate').all()

    @classmethod
    def get_specific_loan(cls, loan_id):
        from mongoengine.queryset import InvalidQueryError
        try:
            return cls.objects.get(id=loan_id)
        except InvalidQueryError:
            return None
        except cls.DoesNotExist:
            return None
    
    def renew_loan(self):
        if self.returnDate is None:
            new_borrow_date = generate_valid_loan_date(self.borrowDate)
            self.renewCount += 1
            self.borrowDate = datetime.combine(new_borrow_date, datetime.min.time())
            self.save()
            return True
        return False
        
    def return_loan(self):
        if self.returnDate is None:
            if self.book.return_book(): 
                random_return_date = generate_valid_loan_date(datetime.utcnow())
                self.returnDate = datetime.combine(random_return_date, datetime.min.time())
                self.save()
                return True
            return False
        return False 

    def delete_loan_document(self):
        if self.returnDate is not None:
            self.delete()
            return True
        return False
    
    @property # helper property to quickly check if a loan is unreturned
    def is_active(self):
        return self.returnDate is None
    
    @property # calculates the due date (+14 days)
    def due_date(self):
        return self.borrowDate + timedelta(days=14)
        
    @property # check if loan is active and past due date
    def is_overdue(self):
        return self.is_active and (self.due_date < datetime.utcnow())

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