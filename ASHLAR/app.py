from flask import Flask, render_template, request, redirect, url_for, send_file, flash, make_response
import os
import sqlite3
import io
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('responses.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS saturn (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            files TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    keyword = request.form.get('keyword')
    results = None

    if keyword:
        conn = get_db_connection()
        results = conn.execute(
            "SELECT * FROM saturn WHERE timestamp LIKE ? OR prompt LIKE ? OR response LIKE ?",
            ('%' + keyword + '%', '%' + keyword + '%', '%' + keyword + '%')
        ).fetchall()
        conn.close()

    return render_template('search.html', results=results, keyword=keyword)

@app.route('/notes', methods=['GET', 'POST'])
def notes():
    conn = get_db_connection()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        files = request.files.getlist('files')

        file_paths = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join('static', 'uploads', filename)
                file.save(filepath)
                file_paths.append(filepath)

        conn.execute('INSERT INTO notes (title, content, files) VALUES (?, ?, ?)',
                     (title, content, ','.join(file_paths)))
        conn.commit()
        flash('Note added successfully!', 'success')
        return redirect(url_for('notes'))

    notes = conn.execute('SELECT * FROM notes').fetchall()
    conn.close()
    return render_template('notes.html', notes=notes)

@app.route('/note/<int:note_id>')
def view_note(note_id):
    conn = get_db_connection()
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    conn.close()
    if not note:
        flash('Note not found', 'danger')
        return redirect(url_for('notes'))
    return render_template('view_note.html', note=note)

@app.route('/update_note/<int:note_id>', methods=['GET', 'POST'])
def update_note(note_id):
    conn = get_db_connection()
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        files = request.files.getlist('files')

        file_paths = note['files'].split(',') if note['files'] else []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join('static', 'uploads', filename)
                file.save(filepath)
                file_paths.append(filepath)
        
        conn.execute('UPDATE notes SET title = ?, content = ?, files = ? WHERE id = ?',
                     (title, content, ','.join(file_paths), note_id))
        conn.commit()
        flash('Note updated successfully!', 'success')
        return redirect(url_for('view_note', note_id=note_id))

    conn.close()
    return render_template('update_note.html', note=note)

@app.route('/delete_note/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    conn.commit()
    conn.close()
    flash('Note deleted successfully!', 'success')
    return redirect(url_for('notes'))

@app.route('/export/<int:row_id>', methods=['GET'])
def export(row_id):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM saturn WHERE id = ?', (row_id,)).fetchone()
    conn.close()

    if row:
        content = f"Timestamp: {row['timestamp']}\n\nPrompt: {row['prompt']}\n\nResponse:\n{row['response']}"
        response = make_response(content)
        response.headers['Content-Disposition'] = f'attachment; filename={row["prompt"]}.txt'
        response.mimetype = 'text/plain'
        return response
    else:
        flash('Record not found', 'danger')
        return redirect(url_for('search'))

@app.route('/add_note', methods=['GET', 'POST'])
def add_note():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        files = request.files.getlist('files')

        file_paths = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join('static', 'uploads', filename)
                file.save(filepath)
                file_paths.append(filepath)

        conn = get_db_connection()
        conn.execute('INSERT INTO notes (title, content, files) VALUES (?, ?, ?)',
                     (title, content, ','.join(file_paths)))
        conn.commit()
        conn.close()
        flash('Note added successfully!', 'success')
        return redirect(url_for('notes'))

    return render_template('add_note.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Implement authentication logic here
        return redirect(url_for('index'))  # Redirect on successful login
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                         (username, password))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose another.', 'danger')
        finally:
            conn.close()

    return render_template('register.html')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'mp3', 'mp4'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
