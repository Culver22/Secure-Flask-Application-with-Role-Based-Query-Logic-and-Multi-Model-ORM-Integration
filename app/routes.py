from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Post
from . import db
from sqlalchemy import text

main = Blueprint('main', __name__, template_folder='templates')

def client_ip():
    # returns the client IP. If behind a proxy, X-Forwarded-For may contain the original IP.
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
        current_app.logger.info('Successful login | ip=%s | username=%s | role=%s | id=%s',
                                client_ip(), username, user.role, user.id)
        flash('Login successful', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    # implemented for testing of data, instead of having to re-run the program
    username = current_user.username
    logout_user()
    current_app.logger.info('Successful logout | ip=%s | username=%s', client_ip(), username)
    flash('Successfully logged out')
    return redirect(url_for('main.login'))  # redirect the user back to login

@main.route('/dashboard')
@login_required
def dashboard():

    role = current_user.role

    if role == 'admin':
        # all fields
        posts = Post.query.order_by(Post.id).all()
        current_app.logger.info('Successful dashboard | ip=%s | username=%s | role=%s | query=all_posts_full',
                                client_ip(), current_user.username, role)
        return render_template('dashboard.html', posts=posts, view='admin')

    if role == 'moderator':
        # limited fields: post id, post title, author username
        rows = (db.session.query(Post.id, Post.title, User.username.label('author'))
                .join(User, Post.author_id==User.id)
                .order_by(Post.id).all())
        current_app.logger.info('Successful dashboard | ip=%s | username=%s | role=%s | query=all_posts_limited',
                                client_ip(), current_user.username, role)
        return render_template('dashboard.html', rows=rows, view='moderator')

    # else role must be user
    posts = Post.query.filter_by(author_id=current_user.id).order_by(Post.id).all()
    current_app.logger.info(
        "Dashboard accessed | ip=%s | username=%s | role=%s | query=user_posts",
        client_ip(), current_user.username, role)

    return render_template('dashboard.html', posts=posts, view='user')

@main.route('/search', methods=['POST'])
@login_required
def search():
    # secure raw SQL using bound parameters

    # get user input
    search_term = request.form.get('search_term')
    role = current_user.role

    # bind parameter dictionary, which will be safely inserted into the query
    params = {'pattern': f'%{search_term}%'}

    if role == "admin":
        # admin: search ALL posts, full details
        sql_statement = text("""
                   SELECT p.id, p.title, p.content, p.author_id, u.username AS author
                   FROM post AS p
                   JOIN user AS u ON p.author_id = u.id
                   WHERE LOWER(p.title) LIKE :pattern OR LOWER(p.content) LIKE :pattern
                   ORDER BY p.id
                   """)
    elif role == "moderator":
        # Moderator: search ALL posts, LIMITED fields
        sql_statement = text("""
                   SELECT p.id, p.title, u.username AS author
                   FROM post AS p
                   JOIN user AS u ON p.author_id = u.id
                   WHERE LOWER(p.title) LIKE :pattern OR LOWER(p.content) LIKE :pattern
                   ORDER BY p.id
                   """)
    else:
        params["uid"] = current_user.id  # bind user scope

        # User: ONLY own posts, full details
        sql_statement = text("""
                   SELECT p.id, p.title, p.content, p.author_id, u.username AS author
                   FROM post AS p
                   JOIN user AS u ON p.author_id = u.id
                   WHERE (LOWER(p.title) LIKE :pattern OR LOWER(p.content) LIKE :pattern)
                    AND p.author_id = :uid
                   ORDER BY p.id
                   """)

    # log the SQL and the bound parameters
    current_app.logger.info(
        "Executing raw SQL search | ip=%s | username=%s | role=%s | id=%s | sql=%s | params=%s",
        client_ip(), current_user.username, current_user.role, current_user.id, sql_statement.text, params )

    rows = db.session.execute(sql_statement, params).fetchall()

    # build simple dicts for template rendering
    results = [
        {
            "id": r.id,
            "title": r.title,
            "content": r.content,
            "author_id": r.author_id,
            "author": r.author,
        }
        for r in rows
    ]

    current_app.logger.info(
        "Search completed | ip=%s | username=%s | role=%s | id=%s | matches=%d",
        client_ip(), current_user.username, current_user.role, current_user.id, len(results)
    )

    # reuse the dashboard and keep role context for the page header
    return render_template('dashboard.html',
                           view=current_user.role,
                           search_term=search_term,
                           search_results=results)
