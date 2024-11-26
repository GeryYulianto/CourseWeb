from database import *
from flask import *
from features.flask_app import FlaskApp

class AuthFeatures(FlaskApp):
    def login(self):
        if request.method == 'POST':
            pass
            # return render_template()
        else:
            return render_template('login_page.html')
    
    def home(self):
        #Kalo belom login
        if not session.get('name'):
            return redirect('/login')
        
        return render_template('homepage.html')

        
    def add_endpoint_auth(self):
        self.add_endpoint('/login', 'login', self.login, ['GET', 'POST'])
        self.add_endpoint('/', 'home', self.home, ['GET'])