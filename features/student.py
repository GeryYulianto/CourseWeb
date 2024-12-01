# FILE: student.py
from flask import render_template, redirect, url_for, session
from features.flask_app import FlaskApp
from database import query_db

class StudentFeatures(FlaskApp):
    def student_dashboard(self):
        if not session.get('email') or session.get('role') != 'student':
            return redirect(url_for('home'))
        return render_template('student/dashboard.html')

    def student_courses(self):
        if not session.get('email') or session.get('role') != 'student':
            return redirect(url_for('home'))
        enrolled_courses = query_db('SELECT * FROM EnrolledCourse WHERE student_id = ?', [session.get('id_peserta')])
        return render_template('student/courses.html', courses=enrolled_courses)

    def student_progress(self):
        if not session.get('email') or session.get('role') != 'student':
            return redirect(url_for('home'))
        progress_data = query_db('SELECT * FROM StudentProgress WHERE student_id = ?', [session.get('id_peserta')])
        return render_template('student/progress.html', progress=progress_data)

    def student_achievements(self):
        if not session.get('email') or session.get('role') != 'student':
            return redirect(url_for('home'))
        achievements = query_db('SELECT * FROM Achievement WHERE student_id = ?', [session.get('id_peserta')])
        return render_template('student/achievements.html', achievements=achievements)

    def student_course_detail(self, course_id):
        if not session.get('email') or session.get('role') != 'student':
            return redirect(url_for('home'))
        course = query_db('SELECT * FROM Course WHERE id = ?', [course_id], one=True)
        if not course:
            return redirect(url_for('home'))
        return render_template('student/course_detail.html', course=course)

    def take_quizs(self, quiz_id):
        if not session.get('email') or session.get('role') != 'student':
            return redirect(url_for('home'))
        quiz = query_db('SELECT * FROM Quiz WHERE id = ?', [quiz_id], one=True)
        if not quiz:
            return redirect(url_for('home'))
        return render_template('student/quiz.html', quiz=quiz)

    def submit_quiz(self, quiz_id):
        if not session.get('email') or session.get('role') != 'student':
            return redirect(url_for('home'))
        # Handle quiz submission logic here
        pass

    def add_endpoints_student(self):
        self.add_endpoint('/student/dashboard', 'student_dashboard', self.student_dashboard, methods=['GET'])
        self.add_endpoint('/student/courses', 'student_courses', self.student_courses, methods=['GET'])
        self.add_endpoint('/student/progress', 'student_progress', self.student_progress, methods=['GET'])
        self.add_endpoint('/student/achievements', 'student_achievements', self.student_achievements, methods=['GET'])
        self.add_endpoint('/student/course/<int:course_id>', 'student_course_detail', self.student_course_detail, methods=['GET'])
        self.add_endpoint('/student/quiz/<int:quiz_id>', 'take_quizs', self.take_quizs, methods=['GET'])
        self.add_endpoint('/student/quiz/<int:quiz_id>/submit', 'submit_quiz', self.submit_quiz, methods=['POST'])