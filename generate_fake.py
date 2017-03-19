from app import db
from app.models import Role, User, Follow, Post, Comment


def generate_me():
    user = User(
        username='a188616786a',
        email='a188616786a@163.com',
        password='00432791',
        confirmed=True,
        role=Role.query.filter_by(name='Administrator').first()
    )
    db.session.add(user)
    db.session.commit()


def init_db():
    print 'drop all tables...',
    db.drop_all()
    print 'done\ncreate all tables...',
    db.create_all()
    print 'done\ninsert roles...',
    Role.insert_roles()
    print 'done\ninsert me...',
    generate_me()
    print 'done\ninsert users...',
    User.generate_fake()
    print 'done\ninsert follows...',
    Follow.generate_fake()
    print 'done\ninsert posts...',
    Post.generate_fake()
    print 'done\ninsert comments...',
    Comment.generate_fake()
    print 'done'
