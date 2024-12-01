from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)  

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), nullable=False)
    value = db.Column(db.Integer, nullable=False)

# Routes
@app.route('/request-certificate/<int:participant_id>', methods=['GET'])
def request_certificate(participant_id):
    # Check participant
    participant = Participant.query.get(participant_id)
    if not participant:
        return jsonify({'error': 'Participant not found'}), 404

    # Check payment
    payment = Payment.query.filter_by(participant_id=participant_id).first()
    if not payment or payment.status != 'paid':
        return jsonify({'error': 'Payment not completed'}), 400

    # Get score
    score = Score.query.filter_by(participant_id=participant_id).first()
    if not score:
        return jsonify({'error': 'Score not found'}), 404

    # Generate certificate
    return render_template('sertifikat.html', 
                           participant=participant, 
                           payment=payment, 
                           score=score)

@app.route('/admin/manage-payments', methods=['GET'])
def manage_payments():
    participant_id = request.args.get('participant_id')
    payment = None
    if participant_id:
        payment = Payment.query.filter_by(participant_id=participant_id).first()
    return render_template('manage_payment_page.html', payment=payment)

@app.route('/payment', methods=['POST'])
def process_payment():
    participant_id = request.form['participant_id']
    amount = request.form['amount']
    new_payment = Payment(
        participant_id=participant_id,
        status='paid'
    )
    db.session.add(new_payment)
    db.session.commit()
    return redirect(url_for('payment_page', participant_id=participant_id))

@app.route('/invoice/<int:participant_id>', methods=['GET'])
def generate_invoice(participant_id):
    payment = Payment.query.filter_by(participant_id=participant_id).first()
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    invoice = {
        'id': payment.id,
        'participant_id': payment.participant_id,
        'status': payment.status
    }
    return render_template('invoice_page.html', invoice=invoice)

if __name__ == '__main__':
    db.create_all()  # Create tables
    app.run(debug=True)
