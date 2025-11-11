from flask import Flask, request, render_template, redirect, url_for, session, send_from_directory
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'vuln-secret-key'  # DO NOT USE in production
DB = 'vuln.db'
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# init db with a users table and a sample user
def init_db():
    if os.path.exists(DB):
        return
    conn = get_db()
    cur = conn.cursor()
    cur.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, bio TEXT)')
    cur.execute("INSERT INTO users (username,password,bio) VALUES ('alice','password123','Hello, I am Alice')")
    cur.execute("INSERT INTO users (username,password,bio) VALUES ('bob','hunter2','Bob here')")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

# Vulnerable login: builds SQL by concatenation (SQLi)
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username','')
        password = request.form.get('password','')
        conn = get_db()
        # VULNERABLE: string concatenation
        q = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
        print('Query:', q)
        cur = conn.execute(q)
        row = cur.fetchone()
        if row:
            session['user_id'] = row['id']
            return redirect(url_for('index'))
        else:
            return 'Login failed', 401
    return render_template('login.html')

# Comment form: vulnerable to XSS - stores comments in memory and renders without escaping
COMMENTS = []
@app.route('/comments', methods=['GET','POST'])
def comments():
    if request.method == 'POST':
        name = request.form.get('name','anonymous')
        comment = request.form.get('comment','')
        # store as-is (vulnerable)
        COMMENTS.append({'name': name, 'comment': comment})
        return redirect(url_for('comments'))
    return render_template('comments.html', comments=COMMENTS)

# File upload: vulnerable - accepts any file and stores with original filename in uploads (could be used to upload HTML/JS)
@app.route('/upload', methods=['GET','POST'])
def upload():
    message = ''
    if request.method == 'POST':
        if 'file' in request.files:
            f = request.files['file']
            filename = secure_filename(f.filename)  # still uses original name
            dest = os.path.join(UPLOAD_FOLDER, filename)
            f.save(dest)
            message = f'Uploaded to {dest}'
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('upload.html', files=files, message=message)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Profile page: broken access control - uses query parameter id to view any profile without checking session
@app.route('/profile')
def profile():
    uid = request.args.get('id')
    conn = get_db()
    if not uid:
        return 'No id provided', 400
    # VULNERABLE: no authorization check
    cur = conn.execute('SELECT id, username, bio FROM users WHERE id = ?', (uid,))
    row = cur.fetchone()
    if not row:
        return 'Not found', 404
    return render_template('profile.html', user=row)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
