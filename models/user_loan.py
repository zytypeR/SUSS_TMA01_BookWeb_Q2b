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
    def create_loan_document(cls, user_obj, book_obj):
        """
        Attempts to create a new Loan document.
        A loan is only created if:
        1. The book has available copies.
        2. The user does not already have an unreturned loan for this book.
        Returns a tuple: (True/False: status, message)
        """
        # Check 1: User does not already have an unreturned loan for this book
        existing_loan = cls.objects(member=user_obj.id, book=book_obj.id, returnDate=None).first()
        if existing_loan:
            return False, f"You already have an active loan for '{book_obj.title}'."

        # Check 2: Book has available copies and update available count
        if book_obj.borrow(): 
            # If book.borrow() returns True, inventory was updated successfully.
            
            # Create the new loan record
            new_loan = cls(member=user_obj, book=book_obj, borrowDate=datetime.utcnow())
            new_loan.save()
            return True, f"Successfully borrowed '{book_obj.title}'."
        else:
            return False, f"Sorry, '{book_obj.title}' is currently out of copies."
        
    @classmethod
    def get_all_loans_for_user(cls, user_obj):
        """
        Retrieves all loan documents (active and returned) for a specific user,
        ordered by borrow date (newest first).
        """
        return cls.objects(member=user_obj.id).order_by('-borrowDate').all()

    @classmethod
    def get_specific_loan(cls, loan_id):
        """
        Retrieves a single Loan document by its MongoDB ID.
        """
        from mongoengine.queryset import InvalidQueryError
        try:
            # Use get() for exact match by ID
            return cls.objects.get(id=loan_id)
        except InvalidQueryError:
            return None
        except cls.DoesNotExist:
            return None
    
    def renew_loan(self):
        """
        Renews an active loan: increments renewCount and updates borrowDate to now.
        Returns True/False (renewal status).
        """
        if self.returnDate is None:
            self.renewCount += 1
            self.borrowDate = datetime.utcnow() # Update borrow date to mark renewal
            self.save()
            return True
        return False
        
    def return_loan(self):
        """
        Marks a loan as returned, updates the book's available count, and sets the returnDate.
        Returns True/False (return status).
        """
        if self.returnDate is None:
            # Update book inventory first. If successful, update the loan record.
            if self.book.return_book(): # This calls the method added in books.py
                self.returnDate = datetime.utcnow()
                self.save()
                return True
            # Failed to update book inventory (e.g., integrity error)
            return False
        return False # Loan was already returned

    def delete_loan_document(self):
        """
        Deletes the Loan document, but only if the book has been returned.
        Returns True/False (delete status).
        """
        if self.returnDate is not None:
            self.delete()
            return True
        return False
    
    @property
    def is_active(self):
        """Helper property to quickly check if a loan is unreturned."""
        return self.returnDate is None

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