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

    def delete_quiz(self, id_kursus, quiz_id):
        if not session.get('email') or session.get('role') != 'instructor':
            return redirect('/login_instructor')
        
        query_db('DELETE FROM quiz WHERE id = ?', [quiz_id])
        query_db('DELETE FROM quiz_question WHERE id_quiz = ?', [quiz_id])
        query_db('DELETE FROM quiz_choice WHERE id_quiz_question IN (SELECT id FROM quiz_question WHERE id_quiz = ?)', [quiz_id])

        return redirect('/instructor/manage-materials/' + str(id_kursus))

    def add_endpoint_quiz(self):
        self.add_endpoint('/instructor/quiz/<int:id_kursus>', 'quiz', self.quiz, ['GET', 'POST'])
        self.add_endpoint('/instructor/quiz/delete/<int:id_kursus>/<int:quiz_id>', 'delete_quiz', self.delete_quiz, ['GET'])
        