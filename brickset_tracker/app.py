from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_restful import Api
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

load_dotenv()
db = SQLAlchemy()

# creates the app and returns it as an object
def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///local.db')
    app.secret_key = os.getenv('SECRET_KEY')

    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)

    from models import User, SetModel, BrandModel, user_sets
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(uid)
    
    # what to do when the user is not logged in
    @login_manager.unauthorized_handler
    def unathorized_callback():
        return redirect(url_for('login'))
    #   return 'No premission!'

    bcrypt = Bcrypt(app)

    # we import the routes, views, models
    from routes import register_routes
    register_routes(app, db,  bcrypt)

    api = Api(app)

    from resources import BrickSets, BrickSet, Brands, Brand, SetSearch
    api.add_resource(BrickSets, '/api/sets') 
    api.add_resource(BrickSet, '/api/sets/<int:id>') # <int:id> name here needs to match what goes into the function
    
    api.add_resource(Brands, '/api/brands')
    api.add_resource(Brand, '/api/brands/<int:id>')

    api.add_resource(SetSearch, '/api/search_sets')

    return app