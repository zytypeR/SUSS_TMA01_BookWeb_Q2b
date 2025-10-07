from flask import render_template, redirect, url_for, Blueprint, request
from .__init__ import app, db, Book 

# Seeding Execution Point
# executes the initialize_db method inside the Book class, seeding the DB if empty.
Book.initialize_db()

# BLUEPRINT
book = Blueprint('book', __name__, template_folder='templates')

# Book Titles page route
@book.route('/booktitles', methods=['GET'])
def book_titles():
    selected_category = request.args.get('category', 'All') 

    all_books = Book.getAllBooks(category_filter=selected_category)
    return render_template ('book_titles.html',
                        all_books=all_books,
                        selected_category=selected_category,
                        panel="BOOK TITLES")

# Book Details page route
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
