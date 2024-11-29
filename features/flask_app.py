from database import *
from flask_session import Session
from flask import *


flask_app = Flask(__name__)

class FlaskApp():
    def __init__(self, app):
        self.app = app
        self.app.config["SESSION_PERMANENT"] = False
        self.app.config["SESSION_TYPE"] = "filesystem"
        Session(app)
        self.init_db()

    def init_db(self):
        with self.app.app_context():
            init_db()

    def add_endpoint(self, endpoint, endpoint_name, handler, methods):
        self.app.add_url_rule(endpoint, endpoint_name, handler, methods=methods)
    
    def run(self):
        self.app.run(debug=True)