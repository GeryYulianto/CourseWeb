import sqlite3
from flask import *

DATABASE = 'course.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    get_db().commit()
    return (rv[0] if rv else None) if one else rv

def init_db():
    with get_db() as db:
        db.execute(''' 
            CREATE TABLE IF NOT EXISTS peserta (
                id_peserta INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                nama_peserta TEXT NOT NULL,
                password TEXT NOT NULL,
                no_telpon TEXT NOT NULL,
                alamat TEXT NOT NULL,
                kota TEXT NOT NULL,
                provinsi TEXT NOT NULL,
                kode_pos INT NOT NULL,
                negara TEXT NOT NULL
            )
        ''')

        db.execute(''' 
            CREATE TABLE IF NOT EXISTS instruktur (
                id_instruktur INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_instruktur TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        db.execute(''' 
            CREATE TABLE IF NOT EXISTS kursus (
                id_kursus INTEGER PRIMARY KEY AUTOINCREMENT,
                id_instruktur INTEGER,
                nama_kursus TEXT NOT NULL,
                FOREIGN KEY (id_instruktur) REFERENCES instruktur(id_instruktur)
            )
        ''')
        
        db.execute(''' 
            CREATE TABLE IF NOT EXISTS materi (
                id_materi INTEGER PRIMARY KEY AUTOINCREMENT,
                id_kursus INTEGER,
                konten_materi TEXT NOT NULL,
                link_youtube_video TEXT,
                FOREIGN KEY (id_kursus) REFERENCES kursus(id_kursus)
            )
        ''')
        db.execute(''' 
            CREATE TABLE IF NOT EXISTS nilai (
                id_peserta INTEGER,
                id_materi INTEGER,
                nilai INT NOT NULL,
                FOREIGN KEY (id_peserta) REFERENCES peserta(id_peserta),
                FOREIGN KEY (id_materi) REFERENCES materi(id_materi)
            )
        ''')
        db.execute(''' 
            CREATE TABLE IF NOT EXISTS pembayaran (
                id_pembayaran INTEGER PRIMARY KEY AUTOINCREMENT,
                id_peserta INTEGER,
                id_kursus INTEGER,
                total_harga INT NOT NULL,
                FOREIGN KEY (id_peserta) REFERENCES peserta(id_peserta),
                FOREIGN KEY (id_kursus) REFERENCES kursus(id_kursus)
            )
        ''')
        db.execute(''' 
            CREATE TABLE IF NOT EXISTS sertifikat (
                id_sertifikat INTEGER PRIMARY KEY AUTOINCREMENT,
                id_peserta INTEGER,
                id_kursus INTEGER,
                keterangan TEXT NOT NULL,
                FOREIGN KEY (id_peserta) REFERENCES peserta(id_peserta),
                FOREIGN KEY (id_kursus) REFERENCES kursus(id_kursus)
            )
        ''')

        db.execute(''' 
            CREATE TABLE IF NOT EXISTS invoice (
                id_invoice INTEGER PRIMARY KEY AUTOINCREMENT,
                id_pembayaran INTEGER,
                id_peserta INTEGER,
                detail_invoice TEXT NOT NULL,
                FOREIGN KEY (id_pembayaran) REFERENCES pembayaran(id_pembayaran),
                FOREIGN KEY (id_peserta) REFERENCES peserta(id_peserta)
            )
        ''')
        db.execute(''' 
            CREATE TABLE IF NOT EXISTS admin (
                id_admin INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        db.execute(''' 
            CREATE TABLE IF NOT EXISTS peserta_has_kursus (
                id_peserta INTEGER,
                id_kursus INTEGER,
                FOREIGN KEY (id_peserta) REFERENCES peserta(id_peserta),
                FOREIGN KEY (id_kursus) REFERENCES kursus(id_kursus)
            )
        ''')
        db.execute(''' 
            CREATE TABLE IF NOT EXISTS all_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS quiz (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_kursus INTEGER,
                title TEXT NOT NULL,
                FOREIGN KEY (id_kursus) REFERENCES kursus(id_kursus)
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS quiz_question (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_quiz INTEGER,
                question TEXT NOT NULL,
                FOREIGN KEY (id_quiz) REFERENCES quiz(id)
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS quiz_choice (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_quiz_question INTEGER,
                choice TEXT NOT NULL,
                is_answer INTEGER CHECK(is_answer IN (0, 1)),
                FOREIGN KEY (id_quiz_question) REFERENCES quiz_question(id)
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS user_has_quiz (
                id_peserta INTEGER,
                id_quiz INTEGER,
                score INTEGER NOT NULL,
                FOREIGN KEY (id_peserta) REFERENCES peserta(id_peserta),
                FOREIGN KEY (id_quiz) REFERENCES quiz(id)
            )
        ''')

        db.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                date TEXT NOT NULL
            )
        ''')

        db.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payment_id INTEGER NOT NULL,
                participant_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY (payment_id) REFERENCES payments(id)
            )
        ''')

        # Create triggers to update all_users table
        db.execute('''
            CREATE TRIGGER IF NOT EXISTS insert_peserta AFTER INSERT ON peserta
            BEGIN
                INSERT INTO all_users (email, password, role)
                VALUES (NEW.email, NEW.password, 'peserta');
            END;
        ''')
        db.execute('''
            CREATE TRIGGER IF NOT EXISTS insert_instruktur AFTER INSERT ON instruktur
            BEGIN
                INSERT INTO all_users (email, password, role)
                VALUES (NEW.email, NEW.password, 'instruktur');
            END;
        ''')
        db.execute('''
            CREATE TRIGGER IF NOT EXISTS insert_admin AFTER INSERT ON admin
            BEGIN
                INSERT INTO all_users (email, password, role)
                VALUES (NEW.email, NEW.password, 'admin');
            END;
        ''')

        # Create triggers to delete from all_users table
        db.execute('''
            CREATE TRIGGER IF NOT EXISTS delete_peserta AFTER DELETE ON peserta
            BEGIN
                DELETE FROM all_users WHERE email = OLD.email AND role = 'peserta';
            END;
        ''')
        db.execute('''
            CREATE TRIGGER IF NOT EXISTS delete_instruktur AFTER DELETE ON instruktur
            BEGIN
                DELETE FROM all_users WHERE email = OLD.email AND role = 'instruktur';
            END;
        ''')
        db.execute('''
            CREATE TRIGGER IF NOT EXISTS delete_admin AFTER DELETE ON admin
            BEGIN
                DELETE FROM all_users WHERE email = OLD.email AND role = 'admin';
            END;
        ''')

        # Create triggers to update all_users table
        db.execute('''
            CREATE TRIGGER IF NOT EXISTS update_peserta AFTER UPDATE ON peserta
            BEGIN
                UPDATE all_users SET email = NEW.email, password = NEW.password WHERE email = OLD.email AND role = 'peserta';
            END;
        ''')
        db.execute('''
            CREATE TRIGGER IF NOT EXISTS update_instruktur AFTER UPDATE ON instruktur
            BEGIN
                UPDATE all_users SET email = NEW.email, password = NEW.password WHERE email = OLD.email AND role = 'instruktur';
            END;
        ''')
        db.execute('''
            CREATE TRIGGER IF NOT EXISTS update_admin AFTER UPDATE ON admin
            BEGIN
                UPDATE all_users SET email = NEW.email, password = NEW.password WHERE email = OLD.email AND role = 'admin';
            END;
        ''')

        db.commit()
#Migrations