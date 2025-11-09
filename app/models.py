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

    # only seed if empty
    if User.query.count() == 0:
        admin = User(username="admin", email="admin@example.com", password="admin123", role="admin")
        moderator = User(username="mod1", email="mod1@example.com", password="mod123", role="moderator")
        user1 = User(username="user1", email="user1@example.com", password="user123", role="user")
        user2 = User(username="user2", email="user2@example.com", password="user456", role="user")

        db.session.add_all([admin, moderator, user1, user2])
        db.session.commit()

    if Post.query.count() == 0:
        admin = User.query.filter_by(username="admin").first()
        mod1 = User.query.filter_by(username="mod1").first()
        u1 = User.query.filter_by(username="user1").first()
        u2 = User.query.filter_by(username="user2").first()

        posts = [
            Post(title="Welcome Post", content="This is the first post.", author_id=admin.id),
            Post(title="Moderator Update", content="Moderator insights here.", author_id=mod1.id),
            Post(title="User Thoughts", content="User1 shares ideas.", author_id=u1.id),
            Post(title="Another User Post", content="User2 contributes.", author_id=u2.id),
        ]
        db.session.add_all(posts)
        db.session.commit()