from features.flask_app import FlaskApp
from features.auth import AuthFeatures
from flask import Flask

flask_app = Flask(__name__)

app = FlaskApp(flask_app)

auth_features = AuthFeatures(flask_app)

auth_features.add_endpoint_auth()

if __name__ == "__main__":
    app.run(debug=True)