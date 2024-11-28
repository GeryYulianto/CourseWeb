from werkzeug.security import generate_password_hash, check_password_hash
from database import *
from flask import *
from features.flask_app import FlaskApp

class AuthFeatures(FlaskApp):
    def login(self):
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            
            user = query_db('SELECT * FROM peserta WHERE email = ?', (email,), one=True)
            
            if user and check_password_hash(user['password'], password):
                session['email'] = email
                session['role'] = 'user'
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
        if not session.get('email') and session.get('role') != 'user':
            return redirect('/login')
        
        return render_template('homepage.html')
    
    def logout(self):
        session.clear()
        return redirect('/')
    
    def register_instructor(self):
        if request.method == 'POST':
            nama = request.form['nama']
            email = request.form['email']
            password = request.form['password']

            # Check if email already exists
            existing_user = query_db('SELECT * FROM all_users WHERE email = ?', (email,), one=True)
            if existing_user:
                return render_template('register_instructor_page.html', error='Email already registered')

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            query_db('INSERT INTO instruktur (nama_instruktur, email, password) VALUES (?, ?, ?)',
                     (nama, email, hashed_password))
            
            return redirect('/login_instructor')
        else:
            return render_template('register_instructor_page.html')

    def login_instructor(self):
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            
            user = query_db('SELECT * FROM instruktur WHERE email = ?', (email,), one=True)
            
            if user and check_password_hash(user['password'], password):
                session['email'] = email
                session['role'] = 'instructor'
                return redirect('/instructor')
            else:
                return render_template('login_instructor_page.html', error='Invalid email or password')
        else:
            return render_template('login_instructor_page.html')
        
    def instructor(self):
        if not session.get('email') and session.get('role') != 'instructor':
            return redirect('/login_instructor')
        
        email = session['email']
        instructor = query_db('SELECT id_instruktur FROM instruktur WHERE email = ?', (email,), one=True)
        if instructor:
            courses = query_db('SELECT * FROM kursus WHERE id_instruktur = ?', (instructor['id_instruktur'],))
            return render_template('instructor_page.html', courses=courses)
        else:
            return redirect('/login_instructor')

    def register_admin(self):
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            # Check if email already exists
            existing_user = query_db('SELECT * FROM all_users WHERE email = ?', (email,), one=True)
            if existing_user:
                return render_template('register_admin_page.html', error='Email already registered')

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            query_db('INSERT INTO admin (email, password) VALUES (?, ?)',
                     (email, hashed_password))
            
            return redirect('/login_admin')
        else:
            return render_template('register_admin_page.html')
    
    def login_admin(self):
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            
            user = query_db('SELECT * FROM admin WHERE email = ?', (email,), one=True)
            
            if user and check_password_hash(user['password'], password):
                session['email'] = email
                session['role'] = 'admin'
                return redirect('/admin')
            else:
                return render_template('login_admin_page.html', error='Invalid email or password')
        else:
            return render_template('login_admin_page.html')
        
    def admin(self):
        if not session.get('email') and session.get('role') != 'admin':
            return redirect('/login_admin')
        
        return render_template('admin_page.html')
    
    def manage_users(self):
        if not session.get('email') and session.get('role') != 'admin':
            return redirect('/login_admin')
        
        users = query_db('SELECT * FROM peserta')
        return render_template('manage_users_page.html', users=users)
        
    def edit_user(self, id_peserta):
        if not session.get('email') and session.get('role') != 'admin':
            return redirect('/login_admin')
        
        if request.method == 'POST':
            id_peserta = request.form['id_peserta']
            email = request.form['email']
            nama = request.form['nama']
            no_telpon = request.form['no_telpon']
            alamat = request.form['alamat']
            kota = request.form['kota']
            provinsi = request.form['provinsi']
            kode_pos = request.form['kode_pos']
            negara = request.form['negara']
            
            query_db('UPDATE peserta SET nama_peserta = ?, no_telpon = ?, alamat = ?, kota = ?, provinsi = ?, kode_pos = ?, negara = ?, email = ? WHERE id_peserta = ?',
                     (nama, no_telpon, alamat, kota, provinsi, kode_pos, negara, email, id_peserta))
            return redirect('/admin/manage-users')
        
        user = query_db('SELECT * FROM peserta WHERE id_peserta = ?', (id_peserta,), one=True)
        return render_template('edit_user_page.html', user=user)
    
    def delete_user(self, id_peserta):
        if not session.get('email') and session.get('role') != 'admin':
            return redirect('/login_admin')
        
        query_db('DELETE FROM peserta WHERE id_peserta = ?', (id_peserta,))
        return redirect('/admin/manage-users')
    
    def add_user(self):
        if not session.get('email') and session.get('role') != 'admin':
            return redirect('/login_admin')
        
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
                return render_template('add_user_page.html', error='Email already registered')

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            query_db('INSERT INTO peserta (email, nama_peserta, password, no_telpon, alamat, kota, provinsi, kode_pos, negara) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                     (email, nama, hashed_password, no_telpon, alamat, kota, provinsi, kode_pos, negara))
            
            return redirect('/admin/manage-users')
        else:
            return render_template('add_user_page.html')
    
    def manage_courses(self):
        if not session.get('email') and session.get('role') != 'admin':
            return redirect('/login_admin')
        
        if request.method == 'POST':
            nama_kursus = request.form['nama_kursus']
            id_instruktur = request.form['id_instruktur']
            
            query_db('INSERT INTO kursus (nama_kursus, id_instruktur) VALUES (?, ?)',
                     (nama_kursus, id_instruktur))
            return redirect('/admin/manage-courses')
        
        courses = query_db('SELECT * FROM kursus INNER JOIN instruktur ON kursus.id_instruktur = instruktur.id_instruktur')
        return render_template('manage_courses_page.html', courses=courses)

    def add_course(self):
        if not session.get('email') and session.get('role') != 'admin':
            return redirect('/login_admin')
        
        if request.method == 'POST':
            nama_kursus = request.form['nama_kursus']
            id_instruktur = request.form['id_instruktur']
            
            query_db('INSERT INTO kursus (nama_kursus, id_instruktur) VALUES (?, ?)',
                     (nama_kursus, id_instruktur))
            return redirect('/admin/manage-courses')
        else:
            instructors = query_db('SELECT * FROM instruktur')
            return render_template('add_course_page.html', instructors=instructors)

    def add_endpoint_auth(self):
        # USER ENDPOINTS ------------------------------------------------------------------------------
        self.add_endpoint('/login', 'login', self.login, ['GET', 'POST'])
        self.add_endpoint('/register', 'register', self.register, ['GET', 'POST'])

        # INSTRUCTURE ENDPOINTS -----------------------------------------------------------------------
        self.add_endpoint('/register_instructor', 'register_instructor', self.register_instructor, ['GET', 'POST'])
        self.add_endpoint('/login_instructor', 'login_instructor', self.login_instructor, ['GET', 'POST'])
        self.add_endpoint('/instructor', 'instructor', self.instructor, ['GET'])

        # HOME ENDPOINTS ------------------------------------------------------------------------------
        self.add_endpoint('/', 'home', self.home, ['GET'])
        self.add_endpoint('/logout', 'logout', self.logout, ['GET'])

        # ADMIN ENDPOINTS ------------------------------------------------------------------------------
        self.add_endpoint('/register_admin', 'register_admin', self.register_admin, ['GET', 'POST'])
        self.add_endpoint('/login_admin', 'login_admin', self.login_admin, ['GET', 'POST'])
        self.add_endpoint('/admin', 'admin', self.admin, ['GET'])
        self.add_endpoint('/admin/manage-users', 'manage_users', self.manage_users, ['GET'])
        self.add_endpoint('/admin/edit-user/<id_peserta>', 'edit_user', self.edit_user, ['GET', 'POST'])
        self.add_endpoint('/admin/delete-user/<id_peserta>', 'delete_user', self.delete_user, ['GET'])
        self.add_endpoint('/admin/add-user', 'add_user', self.add_user, ['GET', 'POST'])
        self.add_endpoint('/admin/manage-courses', 'manage_courses', self.manage_courses, ['GET', 'POST'])
        self.add_endpoint('/admin/add-course', 'add_course', self.add_course, ['GET', 'POST'])

        # COURSES ENDPOINTS ----------------------------------------------------------------------------
        # self.add_endpoint('/courses', 'courses', self.courses, ['GET'])