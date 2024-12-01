from features.flask_app import FlaskApp, render_template, request, redirect, url_for
from features.auth import AuthFeatures
from features.quiz import QuizFeatures
from features.student import StudentFeatures
import sqlite3
from datetime import datetime
from flask import Flask
import sqlite3

flask_app = Flask(__name__)

app = FlaskApp(flask_app)

auth_features = AuthFeatures(flask_app)
quiz_features = QuizFeatures(flask_app)
student_features = StudentFeatures(flask_app)

# Database setup
def init_db():
    with sqlite3.connect('app.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS payments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        participant_id INTEGER NOT NULL,
                        amount REAL NOT NULL,
                        status TEXT NOT NULL DEFAULT 'pending',
                        date TEXT NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS invoices (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        payment_id INTEGER NOT NULL,
                        participant_id INTEGER NOT NULL,
                        amount REAL NOT NULL,
                        date TEXT NOT NULL,
                        FOREIGN KEY (payment_id) REFERENCES payments(id))''')
        conn.commit()

# Routes
@app.route('/admin/manage-payments', methods=['GET'])
def manage_payments():
    participant_id = request.args.get('participant_id')
    payment = None
    if participant_id:
        with sqlite3.connect('app.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM payments WHERE participant_id = ?", (participant_id,))
            payment = c.fetchone()
    return render_template('manage_payment_page.html', payment=payment)

@app.route('/payment', methods=['POST'])
def process_payment():
    participant_id = request.form['participant_id']
    amount = request.form['amount']
    with sqlite3.connect('app.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO payments (participant_id, amount, status, date) VALUES (?, ?, 'completed', ?)",
                  (participant_id, amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
    return redirect(url_for('generate_invoice', participant_id=participant_id))

@app.route('/invoice/<participant_id>', methods=['GET'])
def generate_invoice(participant_id):
    invoice = None
    with sqlite3.connect('app.db') as conn:
        c = conn.cursor()
        c.execute('''
        SELECT p.id AS payment_id, p.amount, p.date, p.participant_id
        FROM payments p WHERE p.participant_id = ?
        ''', (participant_id,))
        payment = c.fetchone()
        if payment:
            invoice = {
                'id': payment[0],
                'amount': payment[1],
                'date': payment[2],
                'participant_id': payment[3]
            }
            c.execute("INSERT INTO invoices (payment_id, participant_id, amount, date) VALUES (?, ?, ?, ?)",
                      (invoice['id'], invoice['participant_id'], invoice['amount'], invoice['date']))
            conn.commit()
    return render_template('invoice_page.html', invoice=invoice)

quiz_features.add_endpoint_quiz()
auth_features.add_endpoint_auth()
student_features.add_endpoints_student()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)