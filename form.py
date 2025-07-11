from wtforms import StringField, PasswordField, BooleanField, SubmitField,TextAreaField, SelectField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Email, EqualTo,Regexp, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[
        DataRequired(message="email is required"),
        Email(message="please enter a valid email")
    ])
    password = PasswordField("Password", validators=[
        DataRequired(message="password is required"),
        Length(min=6, message="password must be at least 6 characters")
    ])
    remember = BooleanField('Remember Me')
    submit = SubmitField("Login")
    
class RegistrationForm(FlaskForm):
    username = StringField("Username", 
                         validators=[DataRequired(), 
                                   Length(min=4, max=20),
                                   Regexp('^\w+$', message="Username must contain only letters, numbers or underscore")
])
    email = StringField("Email", 
                       validators=[DataRequired(), 
                                  Email(),
                                  Length(max=50)
                                  ])
    password = PasswordField("Password", 
                           validators=[DataRequired(), 
                                     Length(min=6),
                                     Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$',message='Password must contain at least 1 uppercase, 1 lowercase, and 1 number')
                                     ])
    confirm_password = PasswordField("Confirm Password", 
                                   validators=[DataRequired(), 
                                              EqualTo('password')])
    submit = SubmitField("Register")
    
    
class ProjectForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])  
    image = FileField("Project Image", validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], "Images only!")  
    ])
    project_url = StringField("Project URL")  
    category = SelectField("Category", choices=[  
        ('Web', 'Web Development'),  
        ('AI', 'AI/ML'),
        ('Mobile', 'Mobile App'),  
        ('other', 'Other')
    ])
    tech_stack = StringField('Technologies Used (comma separated)')
    submit = SubmitField("Add Project") 
    
    
class ContactForm(FlaskForm):
    name = StringField("Your name", validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField("Your email", validators=[DataRequired(), Email(),Length(max=120)])
    subject = StringField("subject", validators=[DataRequired(), Length(min=5, max=200)])
    message = TextAreaField("Message", validators=[
        DataRequired(),
        Length(min=10, max=2000,message="message must be between 10 to 2000 words")
    ])
    submit = SubmitField("send message")
    
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class ProjectForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    image = FileField('Project Image')
    project_url = StringField('Project URL')
    category = SelectField('Category', choices=[
        ('web', 'Web Development'),
        ('mobile', 'Mobile App'),
        ('ai', 'AI/ML'),
        ('data', 'Data Science')
    ])
    tech_stack = StringField('Technologies Used (comma separated)')
    submit = SubmitField('Save Project')
    
    
     