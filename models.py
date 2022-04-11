from main import db

class Paper(db.Model):
    __tablename__ = "user_login"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(15), unique=True)
    user_email = db.Column(db.String())
    user_password = db.Column(db.String(80))

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
    