# FILE: student.py
from flask import *
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
        materis = query_db('SELECT * FROM materi WHERE id_kursus = ?', [course_id])
        quiz = query_db('SELECT * FROM quiz WHERE id_kursus = ?', [course_id]) #can have many quiz
        if not course:
            return redirect(url_for('home'))
        return render_template('student/course_detail.html', course=course, quiz=quiz, materis=materis)

    def take_quizs(self, quiz_id):
        if not session.get('email') or session.get('role') != 'user':
            return redirect(url_for('home'))

        # Fetch the quiz details
        quiz = query_db('SELECT * FROM quiz WHERE id = ?', [quiz_id], one=True)
        if not quiz:
            return redirect(url_for('home'))

        # Check if the student has already submitted the quiz
        submission = query_db(
            'SELECT * FROM user_has_quiz WHERE id_peserta = ? AND id_quiz = ?', 
            [session.get('id_peserta'), quiz_id], 
            one=True
        )
        already_submitted = submission is not None
        score = submission['score'] if already_submitted else None
        print(already_submitted, submission)

        questions = []
        if not already_submitted:
            raw_questions = query_db('SELECT * FROM quiz_question WHERE id_quiz = ?', [quiz_id])
            for question in raw_questions:
                choices = query_db('SELECT * FROM quiz_choice WHERE id_quiz_question = ?', [question['id']])
                questions.append({
                    'id': question['id'],
                    'question': question['question'],
                    'choices': choices
                })

        # If score < 60 and retry is needed, set up retry URL
        retry_url = url_for('retry_quiz', quiz_id=quiz_id) if score is not None and score < 60 else None

        return render_template(
            'student/quiz.html',
            quiz=quiz,
            already_submitted=already_submitted,
            score=score,
            retry_url=retry_url,
            questions=questions
        )



    def submit_quiz(self, quiz_id):
        if not session.get('email') or session.get('role') != 'user':
            return redirect(url_for('home'))

        # Fetch all questions for the quiz
        questions = query_db('SELECT * FROM quiz_question WHERE id_quiz = ?', [quiz_id])

        # Total questions and correct answers counter
        total_questions = len(questions)
        correct_answers = 0

        # Loop through the submitted answers and validate
        for question in questions:
            question_id = question['id']
            submitted_answer_id = request.form.get(f'question_{question_id}')

            if submitted_answer_id:
                # Check if the submitted choice is the correct answer
                is_correct = query_db(
                    'SELECT is_answer FROM quiz_choice WHERE id = ? AND id_quiz_question = ?', 
                    [submitted_answer_id, question_id],
                    one=True
                )
                if is_correct and is_correct['is_answer'] == 1:
                    correct_answers += 1

        # Calculate score
        score = int((correct_answers / total_questions) * 100)
        # Insert or update submission record
        query_db('''
            INSERT INTO user_has_quiz (id_peserta, id_quiz, score) 
            VALUES (?, ?, ?)
        ''', [session.get('id_peserta'), quiz_id, score])

        # Redirect back to the quiz page
        return redirect(url_for('take_quizs', quiz_id=quiz_id))


    def retry_quiz(self, quiz_id):
        if not session.get('email') and session.get('role') != 'student':
            return redirect(url_for('home'))
        # Delete the user's quiz submission
        query_db('DELETE FROM user_has_quiz WHERE id_peserta = ? AND id_quiz = ?', [session.get('id_peserta'), quiz_id])
        return redirect(url_for('take_quizs', quiz_id=quiz_id))


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
        self.add_endpoint('/student/quiz/<int:quiz_id>/retry', 'retry_quiz', self.retry_quiz, methods=['POST'])

