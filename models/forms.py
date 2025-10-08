from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length

class RegForm(FlaskForm):
    # Used for both registration and login validation
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    # Name is only used for registration, but is defined here as per the professor's code structure
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    
    # Checkbox for "Remember Me" on the login form
    remember = BooleanField('Remember Me') 
    submit = SubmitField('Submit')