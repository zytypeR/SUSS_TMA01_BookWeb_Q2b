from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint, request, redirect, render_template, url_for, flash
from ..__init__ import login_manager 
from ..models.user_loan import User
from ..models.forms import RegForm, LoginForm

# Set template_folder to look in the main 'templates' folder (up one level)
auth = Blueprint('auth', __name__, template_folder='../templates')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegForm()
    if request.method == 'POST':
        # Use form.validate_on_submit() for standard Flask-WTF validation and submission check
        if form.validate_on_submit(): 
            existing_user = User.getUser(email=form.email.data)
            if not existing_user:
                
                # --- NEW AVATAR AND ADMIN LOGIC START ---
                # 1. Determine Admin Status and Avatar File
                is_admin = False
                avatar_file = 'default-avatar.png'
                
                if form.email.data == 'admin@lib.sg':
                    is_admin = True
                    avatar_file = 'admin.jpeg' # Set admin's specific avatar
                # --- NEW AVATAR AND ADMIN LOGIC END ---
                
                # 2. Hash Password
                hashpass = generate_password_hash(form.password.data, method='sha256')
                
                # 3. Create the User object directly with the new fields
                new_user = User(
                    email=form.email.data,
                    password=hashpass,
                    name=form.name.data,
                    is_admin=is_admin,       # <--- NEW FIELD
                    avatar_file=avatar_file   # <--- NEW FIELD
                )
                
                # 4. Save the user to the database
                new_user.save() 
                
                # Removed the static User.createUser() call:
                # User.createUser(email=form.email.data, password=hashpass, name=form.name.data)
                
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('auth.login'))
            else:
                form.email.errors.append("User already existed")
                # Fall through to render_template below to show errors
    
    return render_template('register.html', form=form, panel="REGISTER")

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            check_user = User.getUser(email=form.email.data)
            if check_user:
                # Use check_user.password because check_user is now a MongoEngine User object
                if check_password_hash(check_user.password, form.password.data):
                    # Uses form.remember.data for 'Remember Me' functionality
                    login_user(check_user, remember=form.remember.data)
                    # Redirect to your book titles page
                    return redirect(url_for('book.book_titles'))    
                else:
                    form.password.errors.append("User Password Not Correct")
            else:
                form.email.errors.append("No Such User")
    
    return render_template('login.html', form=form, panel="LOGIN")

@auth.route('/logout', methods = ['GET'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    # Redirect to your book titles page
    return redirect(url_for('book.book_titles'))

# NOTE: The load_user function is placed in __init__.py where the login_manager is initialized.