from flask import Flask, render_template, request, redirect, url_for, flash
from aws_admin import UserManager  # Adjusted import

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your secret key

admin = UserManager()  # Adjusted to use UserManager

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

if __name__ == '__main__':
    app.run(debug=True)
