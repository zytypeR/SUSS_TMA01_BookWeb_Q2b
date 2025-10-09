from flask import render_template, redirect, url_for, Blueprint, request, flash
from .__init__ import app, db, Book 
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