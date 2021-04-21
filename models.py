from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User model"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String(20), nullable=False, unique=True, primary_key=True)

    password = db.Column(db.Text, nullable=False)

    email = db.Column(db.String(50), nullable=False, unique=True)

    first_name = db.Column(db.String(30), nullable=False)

    last_name = db.Column(db.String(30), nullable=False)

    @classmethod
    def register(cls, username, pwd, email, first_name, last_name):

        hashedpw = bcrypt.generate_password_hash(pwd)
        thing = hashedpw.decode("utf8")

        return cls(username=username, password=thing, email=email, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate(cls, username, pwd):

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            return u
        else:
            return False 

class Feedback(db.Model):

    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.String(100), nullable=False)

    content = db.Column(db.Text, nullable=False)

    username = db.Column(db.String(30), db.ForeignKey('users.username'))

    user = db.relationship('User', backref="user")

# id - a unique primary key that is an auto incrementing integer
# title - a not-nullable column that is at most 100 characters
# content - a not-nullable column that is text
# username - a foreign key that references the username column in the users table