from flask import *
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def home():
    #Kalo belom login
    if not session.get('name'):
        return redirect('/login')
    
    return render_template('homepage.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        pass
        # return render_template()
    else:
        return render_template('login_page.html')

if __name__ == "__main__":
    app.run(debug=True)