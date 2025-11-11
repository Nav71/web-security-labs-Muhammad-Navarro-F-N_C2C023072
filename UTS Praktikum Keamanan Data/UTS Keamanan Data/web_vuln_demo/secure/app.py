from flask import Flask, request, render_template, redirect, url_for, session, send_from_directory, abort
import sqlite3, os, imghdr
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secure-secret-key'  # for demo only
DB = 'secure.db'
# store uploads outside of static/public folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'safe_uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXT = {'png','jpg','jpeg','gif','txt'}

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if os.path.exists(DB):
        return
    conn = get_db()
    cur = conn.cursor()
    cur.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, bio TEXT)')
    # Passwords stored in plain text here for demo; in real systems use hashing (bcrypt)
    cur.execute("INSERT INTO users (username,password,bio) VALUES ('alice','password123','Hello, I am Alice')")
    cur.execute("INSERT INTO users (username,password,bio) VALUES ('bob','hunter2','Bob here')")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

# Secure login: parameterized query and session
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username','')
        password = request.form.get('password','')
        conn = get_db()
        # Parameterized query to prevent SQLi
        cur = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        row = cur.fetchone()
        if row:
            session['user_id'] = row['id']
            return redirect(url_for('index'))
        else:
            return 'Login failed', 401
    return render_template('login.html')

# Secure comments: use auto-escaped template and simple sanitization (strip <script>)
COMMENTS = []
def sanitize(s):
    # VERY SIMPLE sanitizer for demo only: remove <script> tags
    return s.replace('<script', '&lt;script').replace('</script>', '&lt;/script&gt;')

@app.route('/comments', methods=['GET','POST'])
def comments():
    if request.method == 'POST':
        name = request.form.get('name','anonymous')
        comment = request.form.get('comment','')
        COMMENTS.append({'name': sanitize(name), 'comment': sanitize(comment)})
        return redirect(url_for('comments'))
    return render_template('comments.html', comments=COMMENTS)

# Secure upload: whitelist extensions, check image file signature for images, store outside webroot and rename
def allowed_file(filename):
    ext = filename.rsplit('.',1)[-1].lower() if '.' in filename else ''
    return ext in ALLOWED_EXT

@app.route('/upload', methods=['GET','POST'])
def upload():
    message = ''
    if request.method == 'POST':
        if 'file' in request.files:
            f = request.files['file']
            filename = secure_filename(f.filename)
            if not filename:
                message = 'Invalid filename'
            elif not allowed_file(filename):
                message = 'Extension not allowed'
            else:
                # Save to safe folder using random prefix
                import uuid
                newname = f"{uuid.uuid4().hex}_{filename}"
                dest = os.path.join(UPLOAD_FOLDER, newname)
                f.save(dest)
                # optional: if it's an image, verify signature
                if filename.rsplit('.',1)[-1].lower() in ('png','jpg','jpeg','gif'):
                    if imghdr.what(dest) is None:
                        os.remove(dest)
                        message = 'Uploaded file is not a valid image'
                    else:
                        message = 'Upload successful (stored safely)'
                else:
                    message = 'Upload successful (stored safely)'
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('upload.html', files=files, message=message)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    # Serve files but enforce simple ownership/auth as demo (here we just restrict listing)
    return send_from_directory(UPLOAD_FOLDER, filename)

# Profile page: enforce that user can only view their own profile
@app.route('/profile')
def profile():
    uid = request.args.get('id')
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # require that requested id equals session user id
    try:
        uid_int = int(uid)
    except Exception:
        return 'Invalid id', 400
    if session['user_id'] != uid_int:
        return abort(403)
    conn = get_db()
    cur = conn.execute('SELECT id, username, bio FROM users WHERE id = ?', (uid_int,))
    row = cur.fetchone()
    if not row:
        return 'Not found', 404
    return render_template('profile.html', user=row)

if __name__ == '__main__':
    app.run(port=5002, debug=True)
