from flask import render_template, redirect, url_for, Blueprint, request
# Import the initialized app, db, and the Book model from the local __init__.py
from .__init__ import app, db, Book 

# --- Seeding Execution Point (Q2b Requirement) ---
# This executes the initialize_db method inside the Book class, seeding the DB if empty.
Book.initialize_db()

# BLUEPRINT
book = Blueprint('book', __name__, template_folder='templates')

# Route for the main Book Titles page
@book.route('/booktitles', methods=['GET'])
def book_titles():
    selected_category = request.args.get('category', 'All') 

    all_books = Book.getAllBooks(category_filter=selected_category)
    return render_template ('book_titles.html',
                        all_books=all_books,
                        selected_category=selected_category,
                        panel="BOOK TITLES")

# Route for the Book Details page
@book.route('/viewBookDetail/<title>')
def view_book_detail(title):
    book_details = Book.getBookByTitle(title)

    if book_details is None:
        return redirect(url_for('book.book_titles'))
    return render_template('book_details.html',
                           book=book_details,
                           panel="BOOK DETAILS")

# register BLUEPRINT and route 
app.register_blueprint(book)

# set application to open on the Book Titles page
@app.route('/')
def home():
    return redirect(url_for('book.book_titles'))
