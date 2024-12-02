from features.flask_app import FlaskApp
from features.auth import AuthFeatures
from features.quiz import QuizFeatures
from features.student import StudentFeatures
from features.sertificate import Certificate
from flask import Flask

flask_app = Flask(__name__)

app = FlaskApp(flask_app)

auth_features = AuthFeatures(flask_app)
quiz_features = QuizFeatures(flask_app)
student_features = StudentFeatures(flask_app)
certificate = Certificate(flask_app)

quiz_features.add_endpoint_quiz()
auth_features.add_endpoint_auth()
student_features.add_endpoints_student()
certificate.add_endpoints_certificate()

if __name__ == "__main__":
    app.run(debug=True)