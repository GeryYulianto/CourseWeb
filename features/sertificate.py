# FILE: sertificate.py
from datetime import datetime as dt
from flask import *
from features.flask_app import FlaskApp
from database import query_db

class Certificate(FlaskApp):
    def request_certificate(self, id_kursus, id_peserta):
        if not session.get('email') and session.get('role') != 'user':
            return redirect('/login_student')
        
        # Insert request_certificate
        tanggal = dt.now().strftime('%A, %d %B %Y')

        query_db('INSERT INTO sertifikat (id_kursus, id_peserta, keterangan) VALUES (?, ?, ?)',
                (id_kursus, id_peserta, tanggal))
            
        return redirect(url_for('certificate', id_kursus=id_kursus, id_peserta=id_peserta))
        
    def certificate(self, id_kursus, id_peserta):
        if not session.get('email') and session.get('role') != 'user':
            return redirect('/login_student')
        
        # Get certificate
        certificate = query_db('SELECT * FROM sertifikat WHERE id_kursus = ? AND id_peserta = ?',
                                (id_kursus, id_peserta), True)
        
        if not certificate:
            return redirect(url_for('request_certificate', id_kursus=id_kursus, id_peserta=id_peserta))
        
        # Get course
        course = query_db('SELECT * FROM kursus WHERE id_kursus = ?', (id_kursus,), True)
        
        # Get student
        student = query_db('SELECT * FROM peserta WHERE id_peserta = ?', (id_peserta,), True)
        
        # Get instructor
        instructor = query_db('SELECT * FROM instruktur WHERE id_instruktur = ?', (course['id_instruktur'],), True)

        return render_template(
            'certificate.html', 
            certificate=certificate, 
            course=course, 
            student=student, 
            instructor=instructor
        )

    def add_endpoints_certificate(self):
        self.add_endpoint('/request-certificate/<int:id_kursus>/<int:id_peserta>', 'request_certificate', self.request_certificate, ['GET'])
        self.add_endpoint('/certificate/<int:id_kursus>/<int:id_peserta>', 'certificate', self.certificate, ['GET'])