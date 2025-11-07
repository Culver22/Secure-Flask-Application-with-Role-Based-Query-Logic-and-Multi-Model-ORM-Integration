from . import db
from .models import User, Post

# Models will be defined here during implementation.
# No fields or logic are included in starter code.

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