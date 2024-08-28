from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from aws_admin import UserManager

app = Flask(__name__)
app.secret_key = 'your_secret_key'

admin = UserManager()

# Mock user data (for login, replace this with actual user management)
users_db = {
    'admin': 'adminpassword'
}

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users_db and users_db[username] == password:
            session['username'] = username
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_name = request.form['username']
        if user_name:
            try:
                admin.create_user_and_bucket(user_name)
                flash(f"User {user_name} and bucket created successfully!", "success")
            except Exception as e:
                flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('list_users'))
    return render_template('create_user.html')

@app.route('/delete_user/<user_name>', methods=['GET', 'POST'])
def delete_user(user_name):
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if request.form.get('confirm') == 'Yes':
            try:
                admin.destroy_user(user_name)
                flash(f"User {user_name} deleted successfully!", "success")
            except Exception as e:
                flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('list_users'))
        else:
            return redirect(url_for('list_users'))

    # If the request is GET, show the confirmation page
    return render_template('delete_confirmation.html', user_name=user_name)

@app.route('/list_users')
def list_users():
    if 'username' not in session:
        return redirect(url_for('login'))

    users = admin.get_last_50_users()
    return render_template('list_users.html', users=users)

@app.route('/export_credentials/<user_name>')
def export_credentials(user_name):
    if 'username' not in session:
        return redirect(url_for('login'))

    csv_filename = f"{user_name}_credentials.csv"
    csv_file = admin.export_user_credentials_to_csv(user_name, csv_filename)
    if csv_file:
        return send_file(csv_file, as_attachment=True)
    else:
        flash(f"Error: Could not export credentials for user {user_name}.", "danger")
        return redirect(url_for('list_users'))

if __name__ == '__main__':
    app.run(debug=True)
