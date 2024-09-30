"""
Configure the Flask app, register Blueprints (routes).

Last updated: K. Wheelan, April 2024
"""
import os
from flask import Flask
from app.routes import routes_bp
from app.utils.constants import UPLOAD_FOLDER
from dotenv import load_dotenv
from flask_session import Session
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

# Configure Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.static_folder = 'static'

# Registers the blueprint from routes.py to the app
app.register_blueprint(routes_bp)