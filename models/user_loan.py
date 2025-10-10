from mongoengine import Document, StringField, ReferenceField, DateTimeField, IntField, BooleanField
from datetime import datetime, timedelta
from flask_login import UserMixin
from .books import Book 
import random

# Place this helper function at the top of your file, after imports:
def generate_valid_loan_date(start_dt):
    """
    Generates a new date that is 10-20 days after the start_dt, 
    but cannot be later than today's date (datetime.utcnow().date()).
    """
    # 1. Calculate the target date (10-20 days from start_dt)
    random_days = random.randint(10, 20)
    calculated_date = start_dt.date() + timedelta(days=random_days)
    
    # 2. Define the ceiling (today's date, UTC)
    today_utc = datetime.utcnow().date()
    
    # 3. Apply the constraint: the result cannot be later than today_utc
    # This uses the MINIMUM date between the calculated date and today's date.
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
        """
        Attempts to create a new Loan document with a borrow date 10-20 days in the past.
        Returns a tuple: (True/False: status, message)
        """
        # Check 1: User does not already have an unreturned loan for this book
        existing_loan = cls.objects(member=user_obj.id, book=book_obj.id, returnDate=None).first()
        if existing_loan:
            return False, f"You already have an active loan for '{book_obj.title}'."

        # Check 2: Book has available copies and update available count
        if book_obj.borrow(): 
            # --- MODIFICATION FOR PAST DATE REQUIREMENT ---
            # 1. Generate a random number of days between 10 and 20
            past_days = random.randint(10, 20)
            
            # 2. Calculate the borrow date
            borrow_date_past = datetime.utcnow() - timedelta(days=past_days)
            # ----------------------------------------------
            
            # Create the new loan record using the calculated past date
            new_loan = cls(
                member=user_obj, 
                book=book_obj, 
                borrowDate=borrow_date_past # Use the past date
            )
            new_loan.save()
            return True, f"Successfully borrowed '{book_obj.title}'. Enjoy reading!"
        else:
            return False, f"Oops, '{book_obj.title}' is currently out of copies."
        
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
        Renews an active loan: increments renewCount and updates borrowDate 
        to a new, randomly calculated date (10-20 days from old borrowDate, capped at today).
        """
        # Note: You should enforce the max_renewals and is_overdue checks in the Flask route
        if self.returnDate is None:
            # Calculate the new borrow date using the current borrowDate as the start point
            new_borrow_date = generate_valid_loan_date(self.borrowDate)
            
            # Update the loan document
            self.renewCount += 1
            # Convert the date object back to a datetime object for storage
            self.borrowDate = datetime.combine(new_borrow_date, datetime.min.time())
            self.save()
            return True
        return False
        
    def return_loan(self):
        """
        Marks a loan as returned, updates the book's available count, and sets the returnDate 
        to a new, randomly calculated date (10-20 days from now, capped at today).
        """
        if self.returnDate is None:
            # Update book inventory first. If successful, update the loan record.
            if self.book.return_book(): # This calls the method added in books.py
                
                # Calculate the return date using the current UTC time as the start point
                random_return_date = generate_valid_loan_date(datetime.utcnow())
                
                # Update the loan record
                self.returnDate = datetime.combine(random_return_date, datetime.min.time())
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
    
    @property
    def due_date(self):
        """Calculates the due date (14 days after borrow date)."""
        return self.borrowDate + timedelta(days=14)
        
    @property
    def is_overdue(self):
        """Checks if the loan is active AND past its due date."""
        # Only overdue if active and the due date is in the past
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