from flask import render_template, redirect, url_for, Blueprint, request, flash
from .__init__ import app, db, Book, Loan 
from .controllers.auth import auth
from flask_login import current_user, login_required
from .models.forms import NewBookForm
from datetime import datetime

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
    if current_user.is_admin:
        flash("Admin users cannot borrow books.", "warning")
        return redirect(url_for('book.book_titles'))
    try:
        book_obj = Book.objects.get(id=book_id)

    except Exception:
        flash("Book not found.", "danger")
        return redirect(url_for('book.book_titles'))
    status, message = Loan.create_loan_document(current_user, book_obj)
    if status:
        flash(message, "success")
    else:
        flash(message, "warning") 
    return redirect(url_for('book.book_titles'))

@book.route('/return_loan/<loan_id>', methods=['GET'])
@login_required
def return_loan(loan_id):
    loan_obj = Loan.get_specific_loan(loan_id) 

    if not loan_obj:
        flash("Loan record not found.", "danger")
        return redirect(url_for('book.my_loans'))
        
    # check loan belongs to the current user
    if str(loan_obj.member.id) != str(current_user.id):
        flash("Invalid action: This loan is not yours.", "danger")
        return redirect(url_for('book.my_loans'))
        
    # check loan is still active
    if not loan_obj.is_active: 
        flash("Invalid action: This loan has already been returned.", "warning")
        return redirect(url_for('book.my_loans'))

    # generates random returnDate
    if loan_obj.return_loan():
        return_date_str = loan_obj.returnDate.strftime("%d %b %Y")
        flash(f"Successfully returned '{loan_obj.book.title}'. Return Date: {return_date_str}.", "success")
    else:
        flash(f"Could not return '{loan_obj.book.title}'. An error occurred during inventory update.", "danger")

    return redirect(url_for('book.my_loans'))

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

@book.route('/myloans', methods=['GET'])
@login_required
def my_loans():
    if current_user.is_admin:
        flash("Admins do not have loan records to view.", "warning")
        return redirect(url_for('book.book_titles'))
    user_loans = Loan.get_all_loans_for_user(current_user)
    return render_template('my_loans.html',
                            user_loans=user_loans,
                            panel="MY LOANS")

@book.route('/renew_loan/<loan_id>', methods=['GET'])
@login_required
def renew_loan(loan_id):
    loan_obj = Loan.get_specific_loan(loan_id)
    if not loan_obj or str(loan_obj.member.id) != str(current_user.id):
        flash("Loan not found or does not belong to you.", "danger")
        return redirect(url_for('book.my_loans'))
    
    if not loan_obj.is_active:
        flash("Cannot renew a loan that has already been returned.", "warning")
    elif loan_obj.is_overdue:
        flash("Cannot renew an overdue loan. Please return it.", "warning")
    elif loan_obj.renewCount >= 2: 
        flash("Maximum renewal count reached (2 renewals). Please return the book.", "warning")
    else:
        # updates the borrowDate to a new random date
        if loan_obj.renew_loan():
            new_due_date = loan_obj.due_date.strftime("%d %b %Y")
            flash(f"Successfully renewed '{loan_obj.book.title}'. New due date: {new_due_date}.", "success")
        else:
            flash(f"Failed to renew loan for '{loan_obj.book.title}'.", "danger")
    return redirect(url_for('book.my_loans'))

@book.route('/delete_loan/<loan_id>', methods=['GET'])
@login_required
def delete_loan(loan_id):
    loan_obj = Loan.get_specific_loan(loan_id)
    if not loan_obj or str(loan_obj.member.id) != str(current_user.id):
        flash("Loan not found or does not belong to you.", "danger")
        return redirect(url_for('book.my_loans'))

    if loan_obj.is_active: 
        flash("Only returned loans can be deleted from your history.", "warning")
    else:
        book_title = loan_obj.book.title
        if loan_obj.delete_loan_document():
            flash(f"Successfully deleted loan record for '{book_title}'.", "success")
        else:
            flash(f"Failed to delete loan record for '{book_title}'.", "danger")

    return redirect(url_for('book.my_loans'))

app.register_blueprint(book)
app.register_blueprint(auth)

@app.route('/')
def home():
    return redirect(url_for('book.book_titles'))
