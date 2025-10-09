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
@login_required # Ensure only logged-in users can access
def new_book():
    # 1. Admin Check (If not admin, redirect to book titles)
    if not current_user.is_admin:
        flash("You must be an administrator to add new books.", "danger")
        return redirect(url_for('book.book_titles'))

    form = NewBookForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            
            # 2. Process Authors Field (split by comma and strip whitespace)
            author_list = [a.strip() for a in form.authors.data.split(',') if a.strip()]
            
            # 3. Process Description Field (split by newline for paragraphs)
            description_list = [p.strip() for p in form.description.data.split('\n') if p.strip()]

            try:
                # 4. Create and Save the new Book
                new_book = Book(
                    title=form.title.data,
                    authors=author_list, # Use processed list
                    genres=form.genres.data,
                    category=form.category.data,
                    description=description_list, # Use processed list
                    pages=form.pages.data,
                    copies=form.copies.data,
                    # Available is set to copies as it's a new book
                    available=form.copies.data, 
                    url=form.url.data
                )
                new_book.save()
                
                flash(f"Book '{new_book.title}' added successfully!", "success")
                # Remain on the same page (GET request to clear the form)
                return redirect(url_for('book.new_book'))
                
            except Exception as e:
                flash(f"An error occurred while saving the book: {e}", "danger")
        else:
            flash("Please correct the errors in the form.", "danger")


    return render_template('new_book.html', 
                           form=form,
                           panel="ADD BOOK")

app.register_blueprint(book)
app.register_blueprint(auth)

@app.route('/')
def home():
    return redirect(url_for('book.book_titles'))