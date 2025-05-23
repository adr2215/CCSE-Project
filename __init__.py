from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path 

db = SQLAlchemy()
DB_NAME = "Database.db"

def create_app(config=None):
    app = Flask(__name__)
    if config:
        app.config.update(config)
    app.secret_key = 'my_secret_key'
    app.config ['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    #Initialises the database and establishes a secret key

    from home import home
    from auth import auth
    from admin import admin
    from models import get_user

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    #Using the flask_login manager, you can retrieve and load the user being logged in

    @login_manager.user_loader
    def load_user(user_id):
        return get_user(user_id)

    app.register_blueprint(home, url_prefix = '/home')
    app.register_blueprint(auth,url_prefix = '/')
    app.register_blueprint(admin, url_prefix = '/admin')
    #Registration of blueprints and prefixes for the website tree
    create_database(app)

    return app

def create_database(app):
    if not path.exists(DB_NAME):
        with app.app_context():
            db.create_all()
            create_roles(db)
    #If the database is not already present, it is created

def create_roles(db):
    from models import Role
    if not Role.query.filter_by(name='Admin').first():
        admin = Role(id=1, name='Admin')
        db.session.add(admin)
    if not Role.query.filter_by(name='Customer').first():
        customer = Role(id=2, name = 'Customer')
        db.session.add(customer)
    db.session.commit()
    #Establishes the 2 potnetial roles that a user can possess

