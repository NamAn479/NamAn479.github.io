from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='.')
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret-change-me')

# Database helper (SQLite)
DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        name TEXT,
        password_hash TEXT
    )
    ''')
    conn.commit()
    # seed demo users if missing
    cur.execute("SELECT COUNT(*) as c FROM users")
    row = cur.fetchone()
    if row and row['c'] == 0:
        # Use PBKDF2 to hash so it works on systems without hashlib.scrypt
        demo = [
            ('user', 'user@example.com', 'Demo User', generate_password_hash('secret123', method='pbkdf2:sha256')),
            ('alice', None, 'Alice', generate_password_hash('password1', method='pbkdf2:sha256')),
        ]
        cur.executemany('INSERT INTO users (username, email, name, password_hash) VALUES (?,?,?,?)', demo)
        conn.commit()
    conn.close()

# Initialize DB at startup
init_db()


@app.route('/')
def index():
    return send_from_directory('.', 'login.html')


@app.route('/<path:filename>')
def static_files(filename):
    # serve CSS/JS and other static files from working directory
    return send_from_directory('.', filename)


@app.route('/login', methods=['POST'])
def login():
    data = None
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    email = (data.get('email') or '').strip()
    password = data.get('password') or ''

    # basic validation
    if not email or not password:
        return jsonify(success=False, message='Email and password required'), 400

    # lookup user by email or username (case-insensitive)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE lower(email)=? OR lower(username)=?', (email.lower(), email.lower()))
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify(success=False, message='Invalid email or password'), 401

    if not check_password_hash(row['password_hash'], password):
        return jsonify(success=False, message='Invalid email or password'), 401

    # login success: store a friendly display name (fallback to username or email)
    display_name = row['name'] if row['name'] else (row['username'] if row['username'] else row['email'])
    session['user'] = {'id': row['id'], 'name': display_name}
    return jsonify(success=True, message='Logged in', redirect='/welcome')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return send_from_directory('.', 'register.html')

    data = None
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip()
    name = (data.get('name') or '').strip() or None
    password = data.get('password') or ''

    if not username and not email:
        return jsonify(success=False, message='Username or email required'), 400
    if not password or len(password) < 6:
        return jsonify(success=False, message='Password must be at least 6 characters'), 400

    conn = get_db_connection()
    cur = conn.cursor()
    # check uniqueness
    if username:
        cur.execute('SELECT id FROM users WHERE lower(username)=?', (username.lower(),))
        if cur.fetchone():
            conn.close()
            return jsonify(success=False, message='Username already taken'), 400
    if email:
        cur.execute('SELECT id FROM users WHERE lower(email)=?', (email.lower(),))
        if cur.fetchone():
            conn.close()
            return jsonify(success=False, message='Email already registered'), 400

    # Use PBKDF2 to avoid platforms where hashlib.scrypt isn't available
    password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    cur.execute('INSERT INTO users (username, email, name, password_hash) VALUES (?,?,?,?)',
                (username or None, email or None, name or None, password_hash))
    conn.commit()
    user_id = cur.lastrowid
    conn.close()

    # Do not auto-login after registration; require user to sign in.
    return jsonify(success=True, message='Registered. Please sign in.', redirect='/')


@app.route('/welcome')
def welcome():
    user = session.get('user')
    if not user:
        return redirect(url_for('index'))
    # Ensure we have a sensible display name; if missing, try to fetch from DB
    display_name = user.get('name')
    if not display_name:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT name, username, email FROM users WHERE id=?', (user.get('id'),))
            row = cur.fetchone()
            conn.close()
            if row:
                display_name = row['name'] if row['name'] else (row['username'] if row['username'] else row['email'])
                # update session for future
                session['user']['name'] = display_name
        except Exception:
            display_name = 'User'

    return f"<html><head><meta charset=\"utf-8\"><title>Welcome</title></head><body><h1>Welcome, {display_name}</h1><p><a href=\"/logout\">Sign out</a></p></body></html>"


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
