# FILE: student.py
from flask import render_template, redirect, url_for, session
from features.flask_app import FlaskApp
from database import query_db

class StudentFeatures(FlaskApp):
    def student_dashboard(self):
        if not session.get('email') and session.get('role') != 'student':
            return redirect(url_for('home'))
        return render_template('student/dashboard.html')

    def student_courses(self):
        if not session.get('email') and session.get('role') != 'student':
            return redirect(url_for('home'))
        
        email = session.get('email')
        id_student = query_db('SELECT * FROM peserta WHERE email = ?', (email,), one=True)

        enrolled_courses = query_db('SELECT * FROM peserta_has_kursus INNER JOIN kursus ON peserta_has_kursus.id_kursus = kursus.id_kursus WHERE id_peserta = ?', (id_student['id_peserta'],))
        return render_template('student/courses.html', courses=enrolled_courses)

    def student_progress(self):
        if not session.get('email') and session.get('role') != 'student':
            return redirect(url_for('home'))
        progress_data = query_db('SELECT * FROM StudentProgress WHERE id_peserta = ?', [session.get('id_peserta')])
        return render_template('student/progress.html', progress=progress_data)

    def student_achievements(self):
        if not session.get('email') and session.get('role') != 'student':
            return redirect(url_for('home'))
        achievements = query_db('SELECT * FROM Achievement WHERE id_peserta = ?', [session.get('id_peserta')])
        return render_template('student/achievements.html', achievements=achievements)

    def student_course_detail(self, course_id):
        if not session.get('email') and session.get('role') != 'student':
            return redirect(url_for('home'))
        course = query_db('SELECT * FROM kursus WHERE id_kursus = ?', [course_id], one=True)
        if not course:
            return redirect(url_for('home'))
        return render_template('student/course_detail.html', course=course)

    def take_quizs(self, quiz_id):
        if not session.get('email') and session.get('role') != 'student':
            return redirect(url_for('home'))
        quiz = query_db('SELECT * FROM Quiz WHERE id = ?', [quiz_id], one=True)
        if not quiz:
            return redirect(url_for('home'))
        return render_template('student/quiz.html', quiz=quiz)

    def submit_quiz(self, quiz_id):
        if not session.get('email') and session.get('role') != 'student':
            return redirect(url_for('home'))
        # Handle quiz submission logic here
        pass

    def browse_course(self):
        if not session.get('email') and session.get('role') != 'student':
            return redirect(url_for('home'))
        email = session.get('email')
        student = query_db('SELECT * FROM peserta WHERE email = ?', (email,), one=True)
        student_id = student['id_peserta']

        courses = query_db('''
            SELECT * FROM kursus
            WHERE id_kursus NOT IN (
                SELECT id_kursus FROM peserta_has_kursus WHERE id_peserta = ?
            )
        ''', (student_id,))
        return render_template('student/browse_course.html', courses=courses)

    def add_endpoints_student(self):
        self.add_endpoint('/student/', 'student_dashboard', self.student_dashboard, methods=['GET'])
        self.add_endpoint('/student/courses', 'student_courses', self.student_courses, methods=['GET'])
        self.add_endpoint('/student/progress', 'student_progress', self.student_progress, methods=['GET'])
        self.add_endpoint('/student/achievements', 'student_achievements', self.student_achievements, methods=['GET'])
        self.add_endpoint('/student/course/<int:course_id>', 'student_course_detail', self.student_course_detail, methods=['GET'])
        self.add_endpoint('/student/quiz/<int:quiz_id>', 'take_quizs', self.take_quizs, methods=['GET'])
        self.add_endpoint('/student/quiz/<int:quiz_id>/submit', 'submit_quiz', self.submit_quiz, methods=['POST'])
        self.add_endpoint('/student/browse-course', 'browse_course', self.browse_course, methods=['GET'])
