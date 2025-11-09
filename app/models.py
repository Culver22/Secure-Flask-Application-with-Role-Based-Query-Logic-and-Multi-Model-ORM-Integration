from datetime import datetime
from sqlalchemy import Enum
from flask_login import UserMixin
from . import db

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    # establish columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    # there are only three possible roles a user can have
    role = db.Column( Enum("user", "moderator", "admin", name="role_enum", validate_strings=True), nullable=False,
        server_default="user")

    # User should be a one-to-many relationship, and if deleted so should all their posts
    posts = db.relationship("Post", backref="author", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # foreign key is the user id
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"<Post {self.id} '{self.title}'>"


def seed_data():

    if User.query.count() == 0:
        # Sample users with different roles
        admin = User(username='admin', email='admin@example.com', password='admin123', role='admin')
        moderator = User(username='mod1', email='mod1@example.com', password='mod123', role='moderator')
        user1 = User(username='user1', email='user1@example.com', password='user123', role='user')
        user2 = User(username='user2', email='user2@example.com', password='user456', role='user')

        db.session.add_all([admin, moderator, user1, user2])
        db.session.commit()

    if Post.query.count() == 0:
        # Sample posts authored by different users
        post1 = Post(title='Welcome Post', content='This is the first post.', author_id=1)
        post2 = Post(title='Moderator Update', content='Moderator insights here.', author_id=2)
        post3 = Post(title='User Thoughts', content='User1 shares ideas.', author_id=3)
        post4 = Post(title='Another User Post', content='User2 contributes.', author_id=4)

        db.session.add_all([post1, post2, post3, post4])
        db.session.commit()