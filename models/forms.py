from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, NumberRange, URL

class RegForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    remember = BooleanField('Remember Me') 
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me') 
    submit = SubmitField('Submit')

class NewBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=150)])
    
    # Authors: Using TextAreaField for unlimited authors, separated by commas.
    authors = TextAreaField('Authors (separate with comma, e.g., Author 1, Author 2)', validators=[DataRequired()])
    
    # Genres: Using SelectMultipleField for multi-selection.
    genres_choices = [
        "Animals", "Business", "Comics", "Communication", "Dark Academia", 
        "Emotion", "Fantasy", "Fiction", "Friendship", "Graphic Novels", "Grief", 
        "Historical Fiction", "Indigenous", "Inspirational", "Magic", "Mental Health", 
        "Nonfiction", "Personal Development", "Philosophy", "Picture Books", "Poetry", 
        "Productivity", "Psychology", "Romance", "School", "Self Help"
    ]
    genres = SelectMultipleField('Genres (Select all that apply)', choices=[(g, g) for g in genres_choices], validators=[DataRequired()])
    
    # Category: Using SelectField for single selection.
    category_choices = [('Adult', 'Adult'), ('Teens', 'Teens'), ('Children', 'Children')]
    category = SelectField('Category', choices=category_choices, validators=[DataRequired()])
    
    # Description: Using TextAreaField for multiple paragraphs. Instruct admin to separate paragraphs by newlines.
    description = TextAreaField('Description (separate paragraphs with a new line)', validators=[DataRequired()])
    
    pages = IntegerField('Pages', validators=[DataRequired(), NumberRange(min=1)])
    
    copies = IntegerField('Total Copies', validators=[DataRequired(), NumberRange(min=1)])
    
    # URL is for the image
    url = StringField('Image URL', validators=[DataRequired(), URL()])

    submit = SubmitField('Add Book')