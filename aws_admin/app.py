from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from aws_admin import UserManager
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key'

admin = UserManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        user_name = request.form['username']
        if user_name:
            try:
                admin.create_user_and_bucket(user_name)
                flash(f"User {user_name} and bucket created successfully!", "success")
            except Exception as e:
                flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('index'))
    return render_template('create_user.html')

@app.route('/delete_user', methods=['GET', 'POST'])
def delete_user():
    if request.method == 'POST':
        user_name = request.form['username']
        if user_name:
            try:
                admin.destroy_user(user_name)
                flash(f"User {user_name} deleted successfully!", "success")
            except Exception as e:
                flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('index'))
    return render_template('delete_user.html')

@app.route('/list_users')
def list_users():
    users = admin.get_last_50_users()
    return render_template('list_users.html', users=users)

@app.route('/export_credentials/<user_name>')
def export_credentials(user_name):
    csv_filename = f"{user_name}_credentials.csv"
    csv_file = admin.export_user_credentials_to_csv(user_name, csv_filename)
    if csv_file:
        return send_file(csv_file, as_attachment=True)
    else:
        flash(f"Error: Could not export credentials for user {user_name}.", "danger")
        return redirect(url_for('list_users'))

if __name__ == '__main__':
    app.run(debug=True)
