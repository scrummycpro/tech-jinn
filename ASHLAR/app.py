from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import os
import sqlite3
import io
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'mp3', 'mp4'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('tech-career.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_notes_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            files TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

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
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
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
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
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

if __name__ == '__main__':
    create_notes_table()
    app.run(debug=True)
