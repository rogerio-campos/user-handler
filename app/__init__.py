from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
mail = Mail()
s = URLSafeTimedSerializer('your_secret_key')

def create_app():
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    # app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS')
    # app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL')

    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
   
    db.init_app(app)
    mail.init_app(app)

    with app.app_context():
        from .models import User
        db.create_all()

    from .auth import auth
    from .home import home

    # app.register_blueprint(auth)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(home, url_prefix='/')

    return app

