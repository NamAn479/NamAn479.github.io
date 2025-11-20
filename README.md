# Flask Login Demo

This workspace contains a simple front-end login page (`login.html`, `login.css`, `login.js`) and a minimal Flask backend (`app.py`) for demo purposes.

Quick start (macOS / zsh):

1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the Flask app

```bash
python app.py
```

4. Open the login page in your browser

```bash
open http://127.0.0.1:5000/
```

You can also open the registration page at:

```bash
open http://127.0.0.1:5000/register
```

Credentials (demo):

- `user@example.com` / `secret123`
- `alice` / `password1`

You can register new users at `/register`. Registered users are persisted in a small local SQLite database (`users.db`). Passwords are stored hashed (Werkzeug) for demo safety.

Notes:
- This is a demo only. Do not use the in-memory user store or `FLASK_SECRET` for production.
- To change the secret key, set the `FLASK_SECRET` environment variable before running.
- If you want the backend to serve from a different folder or to add persistence, I can add SQLite storage or a proper user management flow.
