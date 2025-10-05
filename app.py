from flask import Flask, render_template, redirect, url_for, Blueprint, request
from models.books import Book 

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_strong_secret_key' 
    app.static_folder = 'assets' 
    class DummyUser:
        is_authenticated = False
    
    app.jinja_env.globals['current_user'] = DummyUser()
    
    return app
app = create_app()

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
