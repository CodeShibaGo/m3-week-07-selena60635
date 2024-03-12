from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from app import db, app, login

class User(UserMixin, db.Model):
    id = sa.Column('id', sa.Integer, primary_key=True)
    username = sa.Column('username', sa.String(64), index=True, unique=True)
    email = sa.Column('email', sa.String(120),  index=True, unique=True)
    password_hash = sa.Column('password_hash', sa.String(256))
    posts: so.WriteOnlyMapped['Post'] = so.relationship(
        back_populates='author')
    about_me = sa.Column('about_me', sa.String(140))
    last_seen = sa.Column('last_seen', sa.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'


class Post(db.Model):
    id = sa.Column('id', sa.Integer, primary_key=True)
    body = sa.Column('body', sa.String(140))
    timestamp = sa.Column('timestamp', sa.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    user_id = sa.Column('user_id', sa.Integer, sa.ForeignKey("user.id"), index=True)
    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)

with app.app_context():
    db.create_all()
    
@login.user_loader
def load_user(id):
    user = db.session.scalars(sa.select(User).from_statement(sa.text(f"SELECT * FROM user WHERE id = {id}"))).first()
    return user

