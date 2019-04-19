from flask import Flask, render_template, redirect, request, send_from_directory, url_for
application = Flask(__name__, static_url_path="")
#, static_url_path="/var/www/ExGenApp/ExGenApp/static"

from app import routes
from flask_sqlalchemy import SQLAlchemy
import models
