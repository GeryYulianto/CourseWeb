from werkzeug.security import generate_password_hash, check_password_hash
from database import *
from flask import *
from features.flask_app import FlaskApp

class AuthFeatures(FlaskApp):
    def login(self):
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            
            user = query_db('SELECT * FROM all_users WHERE email = ?', (email,), one=True)
            
            if user and check_password_hash(user['password'], password):
                session['email'] = email
                return redirect('/')
            else:
                return render_template('login_page.html', error='Invalid email or password')
        else:
            return render_template('login_page.html')
        
    def register(self):
        if request.method == 'POST':
            nama = request.form['nama']
            email = request.form['email']
            password = request.form['password']
            no_telpon = request.form['no_telpon']
            alamat = request.form['alamat']
            kota = request.form['kota']
            provinsi = request.form['provinsi']
            kode_pos = request.form['kode_pos']
            negara = request.form['negara']

            # Check if email already exists
            existing_user = query_db('SELECT * FROM all_users WHERE email = ?', (email,), one=True)
            if existing_user:
                return render_template('register_page.html', error='Email already registered')

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            query_db('INSERT INTO peserta (email, nama_peserta, password, no_telpon, alamat, kota, provinsi, kode_pos, negara) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                     (email, nama, hashed_password, no_telpon, alamat, kota, provinsi, kode_pos, negara))
            
            return redirect('/login')
        else:
            return render_template('register_page.html')
    
    def home(self):
        #Kalo belom login
        if not session.get('email'):
            return redirect('/login')
        
        return render_template('homepage.html')
    
    def logout(self):
        session.pop('email', None)
        return redirect('/')
        
    def add_endpoint_auth(self):
        self.add_endpoint('/login', 'login', self.login, ['GET', 'POST'])
        self.add_endpoint('/register', 'register', self.register, ['GET', 'POST'])
        self.add_endpoint('/', 'home', self.home, ['GET'])
        self.add_endpoint('/logout', 'logout', self.logout, ['GET'])