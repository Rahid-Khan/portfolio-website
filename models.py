from extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    projects = db.relationship('Project', backref='author', lazy=True)
    __table_args__ = (
        db.Index('ix_user_email', 'email', unique=True),
        db.Index('ix_user_username', 'username', unique=True)
    )
    
    def __repr__(self):
        return f"User('{self.id}', '{self.username}', '{self.email}')"

class Project(db.Model):  
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False) 
    image_file = db.Column(db.String(100), nullable=False, default='default.jpg')
    project_url = db.Column(db.String(100))
    category = db.Column(db.String(50))
    tech_stack = db.Column(db.String(200))  # Add this line
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    
    __table_args__ = (
        db.Index('ix_project_user_id', 'user_id'),
        db.Index('ix_project_date_posted', 'date_posted')
    )

    def image_url(self):
        return f"/static/project_images/{self.image_file}"

    def __repr__(self):
        return f"Project('{self.title}', '{self.date_posted}')"
    
class Message(db.Model):
    id= db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100), nullable= False)
    email = db.Column(db.String(150), nullable = False)
    subject = db.Column(db.String(100), nullable = False)
    message = db.Column(db.Text, nullable= False)
    created_At = db.Column(db.DateTime, default = datetime.utcnow)
    is_read = db.Column(db.Boolean, default= False)
    
    def __repr__(self):
        return f"Message ('{self.message}','{self.created_at}')"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))