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
                session['id_peserta'] = user['id_peserta']
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
        
        return render_template('student/dashboard.html')
    
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
            harga_kursus = request.form['harga_kursus']
            
            query_db('INSERT INTO kursus (nama_kursus, id_instruktur, harga_kursus) VALUES (?, ?, ?)',
                        (nama_kursus, id_instruktur, harga_kursus))
            return redirect('/admin/manage-courses')
        else:
            instructors = query_db('SELECT * FROM instruktur')
            return render_template('add_course_page.html', instructors=instructors)

    def edit_course(self, id_kursus):
        if not session.get('email') and session.get('role') != 'admin':
            return redirect('/login_admin')
        
        if request.method == 'POST':
            nama_kursus = request.form['nama_kursus']
            id_instruktur = request.form['id_instruktur']
            harga_kursus = request.form['harga_kursus']

            query_db('UPDATE kursus SET nama_kursus = ?, id_instruktur = ?, harga_kursus = ? WHERE id_kursus = ?', (nama_kursus, id_instruktur, harga_kursus, id_kursus))
            return redirect('/admin/manage-courses')
        
        course = query_db('SELECT * FROM kursus WHERE id_kursus = ?', (id_kursus,), one=True)
        instructors = query_db('SELECT * FROM instruktur')
        return render_template('edit_course_page.html', course=course, instructors=instructors)

    def manage_materials(self, id_kursus):
        if not session.get('email') or session.get('role') != 'instructor':
            return redirect('/login_instructor')

        email = session['email']
        instructor = query_db('SELECT id_instruktur FROM instruktur WHERE email = ?', (email,), one=True)

        if instructor:
            materials = query_db('SELECT * FROM materi WHERE id_kursus = ?', (id_kursus,))
            
            course_name = query_db('SELECT nama_kursus FROM kursus WHERE id_kursus = ?', (id_kursus,), one=True)
            
            quizzes = query_db('''
                SELECT q.id, q.title, 
                    GROUP_CONCAT(qq.question) as questions,
                    COUNT(qq.id) as question_count
                FROM quiz q 
                LEFT JOIN quiz_question qq ON q.id = qq.id_quiz 
                WHERE q.id_kursus = ? 
                GROUP BY q.id, q.title
            ''', (id_kursus,))

            quiz_list = []
            if quizzes:
                for quiz in quizzes:
                    quiz_dict = {
                        'id_quiz': quiz['id'],
                        'judul_quiz': quiz['title'],
                        'questions': quiz['questions'].split(',') if quiz['questions'] else [],
                        'question_count': quiz['question_count']
                    }
                    quiz_list.append(quiz_dict)

            return render_template(
                'manage_materials_page.html',
                materials=materials,
                id_kursus=id_kursus,
                course_name=course_name['nama_kursus'],
                quiz_list=quiz_list
            )
        else:
            return redirect('/login_instructor')
    
    def add_material(self, id_kursus):
        if not session.get('email') or session.get('role') != 'instructor':
            return redirect('/login_instructor')

        if request.method == 'POST':
            konten_materi = request.form['konten_materi']
            link_youtube_video = request.form['link_youtube_video']

            query_db('INSERT INTO materi (id_kursus, konten_materi, link_youtube_video) VALUES (?, ?, ?)',
                    (id_kursus, konten_materi, link_youtube_video))
            return redirect(f'/instructor/manage-materials/{id_kursus}')

        return render_template('add_material_page.html', id_kursus=id_kursus)

    def update_material(self, id_materi):
        if not session.get('email') or session.get('role') != 'instructor':
            return redirect('/login_instructor')

        if request.method == 'POST':
            konten_materi = request.form['konten_materi']
            link_youtube_video = request.form['link_youtube_video']
            id_kursus = request.form['id_kursus']

            query_db('UPDATE materi SET konten_materi = ?, link_youtube_video = ? WHERE id_materi = ?',
                    (konten_materi, link_youtube_video, id_materi))
            return redirect('/instructor/manage-materials/' + id_kursus)

        material = query_db('SELECT * FROM materi WHERE id_materi = ?', (id_materi,), one=True)
        return render_template('edit_material_page.html', material=material)

    def delete_material(self, id_materi, id_kursus):
        if not session.get('email') or session.get('role') != 'instructor':
            return redirect('/login_instructor')

        query_db('DELETE FROM materi WHERE id_materi = ?', (id_materi,))
        return redirect(f'/instructor/manage-materials/{id_kursus}')

    def manage_instructors(self):
        if not session.get('email') and session.get('role') != 'admin':
            return redirect('/login_admin')
        
        instructors = query_db('SELECT * FROM instruktur')
        return render_template('manage_instructor_page.html', instructors=instructors)
    
    def manage_payment(self):
        if not session.get('email') or session.get('role') != 'admin':
            return redirect('/login_admin')

        # Query payment information with participant and course details
        payments = query_db('''
            SELECT 
                p.id_pembayaran, 
                pes.id_peserta, 
                pes.nama_peserta AS peserta_name, 
                k.nama_kursus, 
                p.status
            FROM pembayaran p
            JOIN peserta pes ON p.id_peserta = pes.id_peserta
            JOIN kursus k ON p.id_kursus = k.id_kursus
        ''')
        return render_template('manage_payment_page.html', payments=payments)


    def add_instructor(self):
        if not session.get('email') and session.get('role') != 'admin':
            return redirect('/login_admin')
        
        if request.method == 'POST':
            nama_instruktur = request.form['nama_instruktur']
            email = request.form['email']
            password = request.form['password']

            # Check if email already exists
            existing_user = query_db('SELECT * FROM all_users WHERE email = ?', (email,), one=True)
            if existing_user:
                return render_template('add_instructor_page.html', error='Email already registered')

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            query_db('INSERT INTO instruktur (nama_instruktur, email, password) VALUES (?, ?, ?)',
                     (nama_instruktur, email, hashed_password))
            
            return redirect('/admin/manage-instructors')
        else:
            return render_template('add_instructor_page.html')
        
    def edit_instructor(self, id_instruktur):
        if not session.get('email') and session.get('role') != 'admin':
            return redirect('/login_admin')
        
        if request.method == 'POST':
            nama_instruktur = request.form['nama_instruktur']
            email = request.form['email']
            
            query_db('UPDATE instruktur SET nama_instruktur = ?, email = ? WHERE id_instruktur = ?',
                     (nama_instruktur, email, id_instruktur))
            return redirect('/admin/manage-instructors')
        
        instructor = query_db('SELECT * FROM instruktur WHERE id_instruktur = ?', (id_instruktur,), one=True)
        return render_template('edit_instructor_page.html', instructor=instructor)

    def manage_enrollments(self):
        if not session.get('email') and session.get('role') != 'admin':
            return redirect('/login_admin')
        
        courses = query_db('SELECT * FROM kursus INNER JOIN instruktur ON kursus.id_instruktur = instruktur.id_instruktur')
        enrollments = query_db('SELECT * FROM peserta_has_kursus INNER JOIN peserta ON peserta_has_kursus.id_peserta = peserta.id_peserta INNER JOIN kursus ON peserta_has_kursus.id_kursus = kursus.id_kursus ORDER BY peserta_has_kursus.id_kursus, peserta_has_kursus.id_peserta')
        return render_template('manage_enrollments_page.html', enrollments=enrollments, courses=courses)

    def enroll_student(self, id_kursus):
        if not session.get('email') and session.get('role') != 'admin':
            return redirect('/login_admin')
        
        if request.method == 'POST':
            id_peserta = request.form['id_peserta']
            
            query_db('INSERT INTO peserta_has_kursus (id_peserta, id_kursus) VALUES (?, ?)',
                     (id_peserta, id_kursus))
            return redirect('/admin/manage-enrollments')
        
        course = query_db('SELECT * FROM kursus WHERE id_kursus = ?', (id_kursus,), one=True)
        students = query_db('''
            SELECT * FROM peserta
            WHERE id_peserta NOT IN (
                SELECT id_peserta FROM peserta_has_kursus WHERE id_kursus = ?
            )
        ''', (id_kursus,))
        return render_template('enroll_student_page.html', course=course, students=students)


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
        self.add_endpoint('/admin/edit-course/<id_kursus>', 'edit_course', self.edit_course, ['GET', 'POST'])
        self.add_endpoint('/admin/manage-instructors', 'manage_instructors', self.manage_instructors, ['GET'])
        self.add_endpoint('/admin/add-instructor', 'add_instructor', self.add_instructor, ['GET', 'POST'])
        self.add_endpoint('/admin/edit-instructor/<id_instruktur>', 'edit_instructor', self.edit_instructor, ['GET', 'POST'])
        self.add_endpoint('/admin/manage-enrollments', 'manage_enrollments', self.manage_enrollments, ['GET'])
        self.add_endpoint('/admin/enroll-student/<id_kursus>', 'enroll_student', self.enroll_student, ['GET', 'POST'])
        self.add_endpoint('/admin/manage-payment', 'manage_payment', self.manage_payment, ['GET'])

        # MATERIALS ENDPOINTS ------------------------------------------------------------------------------
        self.add_endpoint('/instructor/manage-materials/<id_kursus>', 'manage_materials', self.manage_materials, ['GET'])
        self.add_endpoint('/instructor/add-material/<id_kursus>', 'add_material', self.add_material, ['GET', 'POST'])
        self.add_endpoint('/instructor/update-material/<id_materi>', 'update_material', self.update_material, ['GET', 'POST'])
        self.add_endpoint('/instructor/delete-material/<id_materi>/<id_kursus>', 'delete_material', self.delete_material, ['GET'])


        # COURSES ENDPOINTS ----------------------------------------------------------------------------
        # self.add_endpoint('/courses', 'courses', self.courses, ['GET'])