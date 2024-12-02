from database import *
from flask import *
from features.flask_app import FlaskApp

class QuizFeatures(FlaskApp):
    def quiz(self, id_kursus):
        if not session.get('email') and session.get('role') != 'instructor':
            return redirect('/login_instructor')
        
        if request.method == 'POST':
            title = request.form['title']
            
            # Insert quiz
            query_db('INSERT INTO quiz (id_kursus, title) VALUES (?, ?)',
                    (id_kursus, title))
            
            # Get the last inserted quiz ID
            last_quiz = query_db('SELECT last_insert_rowid()', one=True)
            quiz_id = last_quiz[0] if last_quiz else None
            
            if not quiz_id:
                flash('Error creating quiz', 'error')
                return redirect(f'/instructor/manage-materials/{id_kursus}')
            
            questions = request.form.getlist('questions[]')
            correct_answers = request.form.getlist('correct_answer[0]')
            print(correct_answers)
            
            # Masukkan choice ke dictionary
            choices = {}
            for i in range(len(questions)):
                choices[i] = request.form.getlist(f'choices[{i}][]')
            
            for i, question in enumerate(questions):
                # Insert question
                query_db('INSERT INTO quiz_question (id_quiz, question) VALUES (?, ?)',
                        (quiz_id, question))
                
                # Get the last inserted question ID
                last_question = query_db('SELECT last_insert_rowid()', one=True)
                question_id = last_question[0] if last_question else None
                
                if not question_id:
                    flash('Error creating question', 'error')
                    continue
                
                question_choices = choices[i]
                for j, choice in enumerate(question_choices):
                    # Mark the correct answer
                    is_correct = 1 if j == int(correct_answers[i]) else 0
                    query_db('INSERT INTO quiz_choice (id_quiz_question, choice, is_answer) VALUES (?, ?, ?)',
                            (question_id, choice, is_correct))

            return redirect(f'/instructor/manage-materials/{id_kursus}')
        else:
            return render_template('quiz_form.html', id_kursus=id_kursus)
    
    def take_quiz(self, course_id, quiz_id):
        if not session.get('email') or session.get('role') != 'student':
            return redirect('/login')
        
        if request.method == 'POST':
            # Get student ID
            student = query_db('SELECT id_peserta FROM peserta WHERE email = ?', 
                            [session['email']], one=True)
            
            if not student:
                flash('Student not found', 'error')
                return redirect(f'/student/course/{course_id}')
            
            correct_answers = 0
            total_questions = 0
            
            # Get all questions for this quiz
            questions = query_db('SELECT id FROM quiz_question WHERE id_quiz = ?', [quiz_id])
            
            for question in questions:
                question_id = question[0]
                student_answer = request.form.get(f'question_{question_id}')
                
                if student_answer:
                    # Check if answer is correct
                    is_correct = query_db('''
                        SELECT 1 FROM quiz_choice 
                        WHERE id_quiz_question = ? AND id = ? AND is_answer = 1
                    ''', [question_id, student_answer], one=True)
                    
                    if is_correct:
                        correct_answers += 1
                    total_questions += 1
            
            # Calculate score (0-100)
            score = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
            
            # Save the score
            query_db('''
                INSERT OR REPLACE INTO user_has_quiz (id_peserta, id_quiz, score)
                VALUES (?, ?, ?)
            ''', [student[0], quiz_id, score])
            
            flash(f'Quiz completed! Your score: {score}%', 'success')
            return redirect(f'/student/course/{course_id}')
        
        else:
            # Get quiz details
            quiz = query_db('''
                SELECT q.*, c.nama_kursus 
                FROM quiz q 
                JOIN kursus c ON q.id_kursus = c.id_kursus 
                WHERE q.id = ? AND q.id_kursus = ?
            ''', [quiz_id, course_id], one=True)
            
            if not quiz:
                flash('Quiz not found', 'error')
                return redirect(f'/student/course/{course_id}')
            
            # Get questions and choices
            questions = query_db('''
                SELECT qq.*, (
                    SELECT qc.id 
                    FROM quiz_choice qc 
                    WHERE qc.id_quiz_question = qq.id AND qc.is_answer = 1
                ) as correct_choice_id
                FROM quiz_question qq 
                WHERE qq.id_quiz = ?
            ''', [quiz_id])
            
            choices = {}
            for question in questions:
                question_choices = query_db('''
                    SELECT * FROM quiz_choice 
                    WHERE id_quiz_question = ?
                ''', [question[0]])
                choices[question[0]] = question_choices
            
            return render_template('take_quiz.html', 
                                quiz=quiz, 
                                questions=questions, 
                                choices=choices,
                                course_id=course_id)

    def delete_quiz(self, id_kursus, quiz_id):
        if not session.get('email') or session.get('role') != 'instructor':
            return redirect('/login_instructor')
        
        query_db('DELETE FROM quiz WHERE id = ?', [quiz_id])
        query_db('DELETE FROM quiz_question WHERE id_quiz = ?', [quiz_id])
        query_db('DELETE FROM quiz_choice WHERE id_quiz_question IN (SELECT id FROM quiz_question WHERE id_quiz = ?)', [quiz_id])

        return redirect('/instructor/manage-materials/' + str(id_kursus))

    def add_endpoint_quiz(self):
        self.add_endpoint('/instructor/quiz/<int:id_kursus>', 'quiz', self.quiz, ['GET', 'POST'])
        self.add_endpoint('/student/course/<int:course_id>/quiz/<int:quiz_id>', 
                        'take_quiz', 
                        self.take_quiz, 
                        ['GET', 'POST'])
        self.add_endpoint('/instructor/quiz/delete/<int:id_kursus>/<int:quiz_id>', 'delete_quiz', self.delete_quiz, ['GET'])
        