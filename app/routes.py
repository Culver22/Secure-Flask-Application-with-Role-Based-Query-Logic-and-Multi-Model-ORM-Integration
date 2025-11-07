from flask import Blueprint, render_template, request, flash, redirect, url_for

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Temporary feedback for testing form submission
        if username and password:
            flash(f"Form submitted with username: {username}")
            return redirect(url_for('main.dashboard'))
        else:
            flash("Please enter both username and password.")

    return render_template('login.html')

@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')