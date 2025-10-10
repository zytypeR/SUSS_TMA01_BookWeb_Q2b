from flask import render_template, redirect, url_for, Blueprint, request, flash
from .__init__ import app, db, Book, Loan
from .controllers.auth import auth
from flask_login import current_user, login_required
from .models.forms import NewBookForm

# executes the initialize_db method inside the Book class, seeding the DB if empty.
Book.initialize_db()

book = Blueprint('book', __name__, template_folder='templates')

@book.route('/booktitles', methods=['GET'])
def book_titles():
    selected_category = request.args.get('category', 'All') 

    all_books = Book.getAllBooks(category_filter=selected_category)
    return render_template ('book_titles.html',
                        all_books=all_books,
                        selected_category=selected_category,
                        panel="BOOK TITLES")

@book.route('/viewBookDetail/<title>')
def view_book_detail(title):
    book_details = Book.getBookByTitle(title)

    if book_details is None:
        return redirect(url_for('book.book_titles'))
    return render_template('book_details.html',
                           book=book_details,
                           panel="BOOK DETAILS")

@book.route('/make_loan/<book_id>', methods=['GET'])
@login_required
def make_loan(book_id):
    """
    Handles the action of borrowing a book by calling the core Loan creation method.
    """
    try:
        book_obj = Book.objects.get(id=book_id)
    except Exception:
        flash("Book not found.", "danger")
        return redirect(url_for('book.book_titles'))

    # Call the encapsulated logic from the Loan model
    status, message = Loan.create_loan_document(current_user, book_obj)

    if status:
        flash(message, "success")
    else:
        flash(message, "warning") # Use warning for user-error like existing loan, danger for inventory error
        
    return redirect(url_for('book.book_titles'))

@book.route('/return_loan/<loan_id>', methods=['GET'])
@login_required
def return_loan(loan_id):
    """
    Handles the action of returning a book using the Loan model's encapsulated logic.
    """
    # 1. Retrieve the loan using the correct helper method name
    loan_obj = Loan.get_specific_loan(loan_id) 

    if not loan_obj:
        flash("Loan record not found.", "danger")
        return redirect(url_for('book.book_titles'))
        
    # Security check 1: Ensure the loan belongs to the current user
    if str(loan_obj.member.id) != str(current_user.id):
        flash("Invalid action: This loan is not yours.", "danger")
        return redirect(url_for('book.book_titles'))
        
    # Security check 2: Ensure the loan is still active
    if not loan_obj.is_active: # Using the new .is_active property from Loan class
        flash("Invalid action: This loan has already been returned.", "warning")
        return redirect(url_for('book.book_titles'))

    # 2. Use the encapsulated return_loan instance method
    if loan_obj.return_loan():
        flash(f"Successfully returned '{loan_obj.book.title}'. Thank you!", "success")
    else:
        # This occurs if the inventory update (book.return_book) fails
        flash(f"Could not return '{loan_obj.book.title}'. An error occurred during inventory update.", "danger")

    return redirect(url_for('book.book_titles'))

@book.route('/new_book', methods=['GET', 'POST'])
@login_required
def new_book():
    if not current_user.is_admin:
        flash("You must be an administrator to add new books.", "danger")
        return redirect(url_for('book.book_titles'))

    form = NewBookForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            book_authors = [name.strip() for name in form.authors.data.split('\n') if name.strip()]
            
            if not book_authors:
                 flash("The book must have at least one author.", "danger")
                 return render_template('new_book.html', form=form, panel="ADD A BOOK")
            
            description_list = [p.strip() for p in form.description.data.split('\n') if p.strip()]

            try:
                new_book = Book(
                    title=form.title.data,
                    authors=book_authors, 
                    genres=form.genres.data,
                    category=form.category.data,
                    description=description_list,
                    pages=form.pages.data,
                    copies=form.copies.data,
                    available=form.copies.data, 
                    url=form.url.data
                )
                new_book.save()
                
                flash(f"Book '{new_book.title}' added successfully!", "success")
                return redirect(url_for('book.new_book'))
                
            except Exception as e:
                flash(f"An error occurred while saving the book: {e}", "danger")
        else:
            flash("Please correct the errors in the form.", "danger")


    return render_template('new_book.html', 
                           form=form,
                           panel="ADD A BOOK")

app.register_blueprint(book)
app.register_blueprint(auth)

@app.route('/')
def home():
    return redirect(url_for('book.book_titles'))