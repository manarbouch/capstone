from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize the SQLAlchemy object
db = SQLAlchemy()

# Initialize the LoginManager object
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # Set up application config
    app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a real secret key
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Your DB URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize db and login_manager
    db.init_app(app)
    login_manager.init_app(app)

    # Set the login_view to the route for logging in
    login_manager.login_view = 'main.login'

    # Define user_loader function
    @login_manager.user_loader
    def load_user(user_id):
        from models import User  # Make sure your User model is imported here
        return User.query.get(int(user_id))

    # Create tables when the app starts (optional, may already be handled by migrations)
    with app.app_context():
        db.create_all()

    return app

