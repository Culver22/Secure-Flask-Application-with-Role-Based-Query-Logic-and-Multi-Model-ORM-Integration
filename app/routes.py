import flask
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Post
from . import db
from sqlalchemy import text

main = Blueprint('main', __name__, template_folder='templates')

def client_ip(request):
    return request.headers.get('X-Forwarded-For', request.remote_addr)

@main.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # safe ORM lookup, parameterised automatically
        user = User.query.filter_by(username=username).first()

        if not user or user.password != password:
            # failed login, username or password
            current_app.logger.warning('Failed login attempt | ip=%s | username=%s', client_ip(), username)
            flash('Invalid username or password')
            return render_template('login.html')

        login_user(user)
        # successful login
        current_app.logger.info('Successful login | ip=%s | username=%s | role=% | id=%s',
                                client_ip(), username, user.role, user.id)
        flash('Login successful')
        return redirect(url_for('main.dashboard'))

    return render_template('login.html')

@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')