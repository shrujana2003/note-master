
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # In SQL, the User class will be represented as user table when given if foreign key


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) # db.Integer is the type of data in the db column
    email = db.Column(db.String(150), unique=True) # email has maxlength 150 chars
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note') # id of every new note must be added to this field

