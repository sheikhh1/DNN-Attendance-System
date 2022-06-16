from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager


db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    TEMP_FOLDER = 'website/static/temp'    
    UPLOAD_FOLDER = 'website/static/upload'  
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['TEMP_FOLDER'] = TEMP_FOLDER
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    #with app.app_context():
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
