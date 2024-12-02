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
            correct_answers = request.form.getlist('correct_answer[]')
            
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
                    print(question_choices, j, choice, correct_answers)
                    # Mark the correct answer
                    is_correct = 1 if j == int(correct_answers[i]) else 0
                    query_db('INSERT INTO quiz_choice (id_quiz_question, choice, is_answer) VALUES (?, ?, ?)',
                            (question_id, choice, is_correct))

            return redirect(f'/instructor/manage-materials/{id_kursus}')
        else:
            return render_template('quiz_form.html', id_kursus=id_kursus)
        
    def update_quiz(self, quiz_id):
        if not session.get('email') or session.get('role') != 'instructor':
            return redirect('/login_instructor')

        if request.method == 'POST':
            # Update quiz title
            title = request.form['title']
            query_db('UPDATE quiz SET title = ? WHERE id = ?', (title, quiz_id))

            # Clear existing questions and choices
            query_db('DELETE FROM quiz_choice WHERE id_quiz_question IN (SELECT id FROM quiz_question WHERE id_quiz = ?)', (quiz_id,))
            query_db('DELETE FROM quiz_question WHERE id_quiz = ?', (quiz_id,))

            # Extract questions and correct answers
            questions = request.form.getlist('questions[]')
            correct_answers = request.form.getlist('correct_answer[]')

            for i, question in enumerate(questions):
                # Insert question
                query_db('INSERT INTO quiz_question (id_quiz, question) VALUES (?, ?)', (quiz_id, question))
                question_id = query_db('SELECT last_insert_rowid()', one=True)[0]

                # Extract choices for the current question
                question_choices = request.form.getlist(f'choices[{i}][]')
                print(question_choices)

                for j, choice in enumerate(question_choices):
                    # Determine if the choice is correct
                    is_correct = 1 if str(j) == correct_answers[i] else 0
                    query_db('INSERT INTO quiz_choice (id_quiz_question, choice, is_answer) VALUES (?, ?, ?)',
                            (question_id, choice, is_correct))

            flash('Quiz updated successfully!', 'success')
            return redirect('/instructor')


        else:
            # Fetch quiz details
            quiz = dict(query_db('SELECT * FROM quiz WHERE id = ?', (quiz_id,), one=True))
            questions = query_db('''
                SELECT q.id AS question_id, q.question, c.id AS choice_id, c.choice, c.is_answer
                FROM quiz_question q
                JOIN quiz_choice c ON q.id = c.id_quiz_question
                WHERE q.id_quiz = ?
            ''', (quiz_id,))

            # Organize questions and choices
            organized_questions = {}
            for row in questions:
                question_id = row['question_id']
                if question_id not in organized_questions:
                    organized_questions[question_id] = {
                        'question': row['question'],
                        'choices': []
                    }
                organized_questions[question_id]['choices'].append({
                    'choice': row['choice'],
                    'is_answer': row['is_answer']
                })

            # Add organized questions to quiz
            quiz['questions'] = list(organized_questions.values())
            print(quiz)
            return render_template('student/edit_quiz_form.html', quiz=quiz)



    def delete_quiz(self, id_kursus, quiz_id):
        if not session.get('email') or session.get('role') != 'instructor':
            return redirect('/login_instructor')
        
        query_db('DELETE FROM quiz WHERE id = ?', [quiz_id])
        query_db('DELETE FROM quiz_question WHERE id_quiz = ?', [quiz_id])
        query_db('DELETE FROM quiz_choice WHERE id_quiz_question IN (SELECT id FROM quiz_question WHERE id_quiz = ?)', [quiz_id])

        return redirect('/instructor/manage-materials/' + str(id_kursus))

    def view_quiz_responses(self,quiz_id):
        if not session.get('email') or session.get('role') != 'instructor':
            return redirect(url_for('home'))

        # Fetch quiz details
        quiz = query_db('SELECT * FROM quiz WHERE id = ?', [quiz_id], one=True)
        if not quiz:
            return redirect(url_for('instructor_dashboard'))

        # Fetch quiz responses
        responses = query_db('''
            SELECT u.nama_peserta as student_name, u.email, uhq.score
            FROM user_has_quiz uhq
            JOIN peserta u ON uhq.id_peserta = u.id_peserta
            WHERE uhq.id_quiz = ?
        ''', [quiz_id])

        return render_template(
            'view_quiz_responses.html',
            quiz=quiz,
            responses=responses
        )


    def add_endpoint_quiz(self):
        self.add_endpoint('/instructor/quiz/<int:id_kursus>', 'quiz', self.quiz, ['GET', 'POST'])
        self.add_endpoint('/instructor/quiz/delete/<int:id_kursus>/<int:quiz_id>', 'delete_quiz', self.delete_quiz, ['GET'])
        self.add_endpoint('/instructor/view-quiz-responses/<int:quiz_id>', 'view_response', self.view_quiz_responses, ['GET'])
        self.add_endpoint('/instructor/update-quiz/<int:quiz_id>', 'update-quiz', self.update_quiz, ['GET', 'POST'])
        