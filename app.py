from flask import Flask, render_template, request, redirect, jsonify, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB limit
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('helpers.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS helpers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            phone TEXT,
            skills TEXT,
            availability TEXT,
            photo TEXT  -- 👈 New column
        )
    ''')
    # Add dummy if empty
    c.execute("SELECT COUNT(*) FROM helpers")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO helpers (name, age, phone, skills, availability, photo) VALUES (?, ?, ?, ?, ?, ?)",
                  ("Sunita Devi", 32, "9876543210", "Maid, Cook", "Morning", "default.jpg"))
    conn.commit()
    conn.close()


# --- Routes ---
@app.route('/')
def home():
    return redirect('index')
@app.route('/register', methods=['POST'])
def register_helper():
    data = request.form
    name = data.get('name')
    age = data.get('age')
    phone = data.get('phone')
    skills = ', '.join(request.form.getlist('skills'))
    availability = data.get('availability')

    # Handle file upload
    file = request.files.get('idproof')
    photo_filename = None

    if file and file.filename:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        photo_filename = filename
    else:
        photo_filename = "default.jpg"  # fallback if no file uploaded

    # Save to DB
    conn = sqlite3.connect('helpers.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO helpers (name, age, phone, skills, availability, photo)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, age, phone, skills, availability, photo_filename))
    conn.commit()
    conn.close()

    return redirect('/success')  # ✅ Always return something


@app.route('/success')
def success():
    return render_template('success.html')
@app.route('/helpers')
def view_helpers():
    conn = sqlite3.connect('helpers.db')
    c = conn.cursor()
    c.execute('SELECT id, name, age, skills, availability, photo FROM helpers')
    helpers = c.fetchall()
    conn.close()
    return render_template('search.html', helpers=helpers)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Hardcoded admin credentials (temporary)
        if email == "admin@citysahayak.com" and password == "admin123":
            return redirect('/admin')
        else:
            return render_template('login.html', error="Invalid credentials. Please try again.")

    return render_template('login.html')
@app.route('/admin')
def admin_dashboard():
    conn = sqlite3.connect('helpers.db')
    c = conn.cursor()
    c.execute('SELECT name, age, phone, skills, availability FROM helpers')
    helpers = c.fetchall()
    conn.close()
    return render_template('admin.html', helpers=helpers)

@app.route('/register-form')
def register_form():
    return render_template('register-helper.html')

@app.route('/profile/<int:helper_id>')
def profile(helper_id):
    conn = sqlite3.connect('helpers.db')
    c = conn.cursor()
    c.execute('SELECT name, age, phone, skills, availability, photo FROM helpers WHERE id=?', (helper_id,))
    helper = c.fetchone()
    conn.close()

    if not helper:
        return "Helper not found", 404

    data = {
        'name': helper[0],
        'age': helper[1],
        'phone': helper[2],
        'skills': helper[3],
        'availability': helper[4],
        'photo': helper[5] if helper[5] else 'default.jpg'
    }

    return render_template('profile.html', helper=data)


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/index')
def index():
    return render_template('index.html')

# --- Run ---
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
