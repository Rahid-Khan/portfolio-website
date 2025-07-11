from flask import Flask
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from extensions import db, bcrypt, login_manager
import os
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from datetime import datetime  # Add this import

def create_app():
    app = Flask(__name__)
    
    csrf = CSRFProtect(app)
    mail = Mail()

    Bootstrap(app)
    app.config['SECRET_KEY'] = "secret key"
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:asdf1234@localhost:5432/result_db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/project_images'  
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-secret-key')
    app.config['SECRET_PASSWORD_SALT'] = os.environ.get('SECRET_PASSWORD_SALT', 'fallback-salt')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Remove hardcoded password    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # Instead of hardcoded email
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Remove the actual password
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    migrate = Migrate(app, db)
    
    # Add this context processor
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}
    
    
    return app

app = create_app()

if os.environ.get('FLASK_ENV') == 'production':
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PREFERRED_URL_SCHEME='https'
    )
from routes import *

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)