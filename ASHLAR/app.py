from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import os
import sqlite3
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

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

@app.route('/search', methods=['GET', 'POST'])
def search():
    results = None
    if request.method == 'POST':
        keyword = request.form.get('keyword')
        if keyword:
            conn = get_db_connection()
            query = "SELECT * FROM logic WHERE prompt LIKE ? OR response LIKE ?"
            results = conn.execute(query, ('%' + keyword + '%', '%' + keyword + '%')).fetchall()
            conn.close()
    return render_template('search.html', results=results)

@app.route('/export', methods=['POST'])
def export():
    prompt = request.form.get('prompt')
    timestamp = request.form.get('timestamp')
    response = request.form.get('response')

    content = f"Timestamp: {timestamp}\n\nPrompt: {prompt}\n\nResponse:\n{response}"

    file_obj = io.BytesIO()
    file_obj.write(content.encode('utf-8'))
    file_obj.seek(0)

    return send_file(file_obj, as_attachment=True, download_name=f"{prompt.replace(' ', '_')}.txt", mimetype='text/plain')

@app.route('/notes', methods=['GET', 'POST'])
def notes():
    conn = get_db_connection()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        files = request.files.getlist('files')
        
        file_paths = []
        for file in files:
            if file:
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                file_paths.append(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn.execute('INSERT INTO notes (title, content, files) VALUES (?, ?, ?)',
                     (title, content, ','.join(file_paths)))
        conn.commit()
        flash('Note added successfully!', 'success')
        return redirect(url_for('notes'))

    notes = conn.execute('SELECT * FROM notes').fetchall()
    conn.close()
    return render_template('notes.html', notes=notes)

@app.route('/download_note/<int:note_id>')
def download_note(note_id):
    conn = get_db_connection()
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    conn.close()

    content = f"Title: {note['title']}\n\nContent:\n{note['content']}"

    file_obj = io.BytesIO()
    file_obj.write(content.encode('utf-8'))
    file_obj.seek(0)

    return send_file(file_obj, as_attachment=True, download_name=f"{note['title'].replace(' ', '_')}.txt", mimetype='text/plain')

if __name__ == '__main__':
    create_notes_table()  # Ensure the notes table exists
    app.run(debug=True)
