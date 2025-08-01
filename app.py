from flask import Flask, render_template, request, redirect, url_for, session
import os
import sqlite3
from datetime import datetime
from model.predict import predict_blood_group
from werkzeug.security import generate_password_hash, check_password_hash
from flask import send_from_directory
from PIL import Image
from werkzeug.utils import secure_filename

# Flask setup
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tif', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------------- DATABASE INITIALIZATION ---------------------- #
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS fingerprints (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 filename TEXT,
                 blood_group TEXT,
                 upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                 )''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL
                 )''')
    conn.commit()
    conn.close()

# -------------------------- AUTH ROUTES -------------------------- #
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
            conn.commit()
            return redirect(url_for('login'))
        except:
            return "⚠️ User already exists."
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            return redirect(url_for('index'))
        else:
            return "❌ Invalid username or password."
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------------------- MAIN PROJECT ROUTE ---------------------- #
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['fingerprint']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            try:
                with Image.open(path) as im:
                    width, height = im.size
                    if width > 512 or height > 512:
                        im.close()
                        os.remove(path)
                        return render_template('index.html', error="❌ Please upload a valid fingerprint scan.")


                    original_ext = filename.rsplit('.', 1)[-1].lower()
                    if original_ext in ['tif', 'tiff']:
                        filename = filename.rsplit('.', 1)[0] + '.png'
                        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        im.save(path)

                predicted_group = predict_blood_group(path)
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                c.execute("INSERT INTO fingerprints (filename, blood_group) VALUES (?, ?)", (filename, predicted_group))
                conn.commit()
                conn.close()
                return render_template('index.html', prediction=predicted_group, image=filename)
            except Exception as e:
                if os.path.exists(path):
                    os.remove(path)
                return f"❌ Invalid image: {e}"
        else:
            return render_template('index.html', error="⚠️ Invalid file type. Please upload a fingerprint image (.png/.jpg/.tif).")

    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ---------------------- MAIN RUNNER ---------------------- #
if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    init_db()
    app.run(debug=True)