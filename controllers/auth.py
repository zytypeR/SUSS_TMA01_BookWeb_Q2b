from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint, request, redirect, render_template, url_for, flash
from ..__init__ import login_manager 
from ..models.user_loan import User
from ..models.forms import RegForm, LoginForm

auth = Blueprint('auth', __name__, template_folder='../templates')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegForm()
    if request.method == 'POST':
        if form.validate_on_submit(): 
            existing_user = User.getUser(email=form.email.data)
            if not existing_user:
                is_admin = False
                avatar_file = 'default-avatar.png'
                
                if form.email.data == 'admin@lib.sg':
                    is_admin = True
                    avatar_file = 'admin.jpeg'
                
                hashpass = generate_password_hash(form.password.data, method='sha256')
                
                new_user = User(
                    email=form.email.data,
                    password=hashpass,
                    name=form.name.data,
                    is_admin=is_admin,      
                    avatar_file=avatar_file   
                )
                new_user.save() 
            
                
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('auth.login'))
            else:
                form.email.errors.append("User already existed")
    
    return render_template('register.html', form=form, panel="REGISTER")

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            check_user = User.getUser(email=form.email.data)
            if check_user:
                # use check_user.password because check_user is now a MongoEngine User object
                if check_password_hash(check_user.password, form.password.data):
                    login_user(check_user, remember=form.remember.data)
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
    return redirect(url_for('book.book_titles'))