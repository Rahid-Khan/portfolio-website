from flask import Flask
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from extensions import db, bcrypt, login_manager
import os
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from datetime import datetime

def create_app():
    app = Flask(__name__)
    
    csrf = CSRFProtect(app)
    mail = Mail()
    Bootstrap(app)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-secret-key')
    app.config['SECRET_PASSWORD_SALT'] = os.environ.get('SECRET_PASSWORD_SALT', 'fallback-salt')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/project_images'
    
    # Mail configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Database configuration for Railway
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Convert postgres:// to postgresql:// if needed (Railway sometimes uses old format)
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://postgres:rBtvlGUmdcEfGVVksCfjGMFThFkOcpDo@postgres.railway.internal:5432/railway', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Fallback: construct from individual Railway variables
        pg_host = os.environ.get('PGHOST')
        pg_port = os.environ.get('PGPORT')
        pg_database = os.environ.get('PGDATABASE')
        pg_user = os.environ.get('PGUSER')
        pg_password = os.environ.get('PGPASSWORD')
        
        if all([postgres.railway.internal, 5432, railway, postgres, rBtvlGUmdcEfGVVksCfjGMFThFkOcpDo]):
            app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{postgres}:{rBtvlGUmdcEfGVVksCfjGMFThFkOcpDo}@{postgres.railway.internal}:{5432}/{railway}"
        else:
            # Final fallback for local development
            app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:asdf1234@localhost:5432/result_db'
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    migrate = Migrate(app, db)
    
    # Add context processor for datetime
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}
    
    return app

app = create_app()

# Production security settings
if os.environ.get('FLASK_ENV') == 'production':
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PREFERRED_URL_SCHEME='https'
    )

# Import routes after app creation
from routes import *

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
