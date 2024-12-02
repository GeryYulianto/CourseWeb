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
        
    def edit_quiz(self, quiz_id):
        if not session.get('email') or session.get('role') != 'instructor':
            return redirect('/login_instructor')
        
        if request.method == 'POST':
            title = request.form['title']
            
            # Update quiz title
            query_db('UPDATE quiz SET title = ? WHERE id = ?', (title, quiz_id))
            
            questions = request.form.getlist('questions[]')
            question_ids = request.form.getlist('question_ids[]')
            correct_answers = request.form.getlist('correct_answer[]')
            
            # Process each question
            for i, question in enumerate(questions):
                question_id = question_ids[i] if i < len(question_ids) else None
                
                if question_id:  # Existing question
                    # Update question
                    query_db('UPDATE quiz_question SET question = ? WHERE id = ?',
                            (question, question_id))
                else:  # New question
                    # Insert new question
                    query_db('INSERT INTO quiz_question (id_quiz, question) VALUES (?, ?)',
                            (quiz_id, question))
                    question_id = query_db('SELECT last_insert_rowid()', one=True)[0]
                
                # Get choices for this question
                choices = request.form.getlist(f'choices[{i}][]')
                choice_ids = request.form.getlist(f'choice_ids[{i}][]')
                
                # Update or insert choices
                for j, choice in enumerate(choices):
                    is_correct = 1 if j == int(correct_answers[i]) else 0
                    
                    if j < len(choice_ids) and choice_ids[j]:  # Existing choice
                        query_db('''UPDATE quiz_choice 
                                SET choice = ?, is_answer = ? 
                                WHERE id = ?''',
                            (choice, is_correct, choice_ids[j]))
                    else:  # New choice
                        query_db('''INSERT INTO quiz_choice 
                                (id_quiz_question, choice, is_answer) 
                                VALUES (?, ?, ?)''',
                            (question_id, choice, is_correct))
            
            # Get course ID for redirect
            course = query_db('SELECT id_kursus FROM quiz WHERE id = ?', (quiz_id,), one=True)
            return redirect(f'/instructor/manage-materials/{course["id_kursus"]}')
        
        else:
            # Fetch quiz data
            quiz = query_db('SELECT * FROM quiz WHERE id = ?', (quiz_id,), one=True)
            questions = query_db('''
                SELECT qq.*, GROUP_CONCAT(qc.id) as choice_ids, 
                    GROUP_CONCAT(qc.choice) as choices,
                    GROUP_CONCAT(qc.is_answer) as answers
                FROM quiz_question qq
                LEFT JOIN quiz_choice qc ON qq.id = qc.id_quiz_question
                WHERE qq.id_quiz = ?
                GROUP BY qq.id
            ''', (quiz_id,))
            
            # Process questions and choices
            processed_questions = []
            for q in questions:
                choices = q['choices'].split(',') if q['choices'] else []
                choice_ids = q['choice_ids'].split(',') if q['choice_ids'] else []
                answers = q['answers'].split(',') if q['answers'] else []
                
                correct_answer = next((str(i) for i, ans in enumerate(answers) if ans == '1'), '0')
                
                processed_questions.append({
                    'id': q['id'],
                    'question': q['question'],
                    'choices': choices,
                    'choice_ids': choice_ids,
                    'correct_answer': correct_answer
                })
            
            course = query_db('SELECT nama_kursus FROM kursus WHERE id_kursus = ?', 
                            (quiz['id_kursus'],), one=True)
            
            return render_template('student/edit_quiz.html',
                                quiz=quiz,
                                questions=processed_questions,
                                course_name=course['nama_kursus'])



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
        self.add_endpoint('/instructor/update-quiz/<int:quiz_id>', 'update-quiz', self.edit_quiz, ['GET', 'POST'])
        