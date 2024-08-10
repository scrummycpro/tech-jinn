from flask import Flask, render_template, request
import sqlite3
import markdown

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('tech-career.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    keyword = ''

    conn = get_db_connection()

    if request.method == 'POST':
        keyword = request.form['keyword'].strip()

        if keyword:  # Ensure keyword is not empty
            try:
                columns = ['id', 'timestamp', 'prompt', 'response']
                query = "SELECT * FROM logic WHERE " + " OR ".join([f"{col} LIKE ?" for col in columns])
                params = [f"%{keyword}%"] * len(columns)

                rows = conn.execute(query, params).fetchall()

                # Convert each row to a dictionary and render the response as Markdown
                for row in rows:
                    row_dict = dict(row)  # Convert the row to a dictionary
                    row_dict['response'] = markdown.markdown(row_dict['response'])  # Convert Markdown to HTML
                    results.append(row_dict)

            except sqlite3.OperationalError as e:
                print("SQLite OperationalError:", e)
        else:
            print("Empty keyword provided.")

    conn.close()

    return render_template('search.html', results=results, keyword=keyword)

if __name__ == '__main__':
    app.run(debug=True)
