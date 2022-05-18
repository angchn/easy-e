from main import db
from flask_login import UserMixin

class Paper(db.Model):
    __tablename__ = "past_papers"
    id = db.Column(db.Integer, primary_key=True)
    paper_file = db.Column(db.Text())
    name = db.Column(db.Text())
    subject = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    standard = db.Column(db.Text())

    subjects = db.relationship('Subjects', backref='papers', lazy=True)

    def __repr__(self):
        return self.paper_file 

class Subjects(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.Text())

    def __repr__(self):
        return self.subject_name

class User(UserMixin, db.Model):
    __tablename__ = "user_login"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    user_name = db.Column(db.String(15), unique=True)
    user_email = db.Column(db.String(50), unique=True)
    user_password = db.Column(db.String(80))

    todo = db.relationship ("Todo", backref='todo')

class Todo(db.Model):
    __tablename__ = "todo"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    user = db.Column(db.Integer(), db.ForeignKey('user_login.id'))

    def __repr__(self):
        return f"<Todo '{self.name}'>"