from main import db

PaperSubject = db.Table('paper_subject',
    db.Column('paper_id', db.Integer, db.ForeignKey('past_papers.id')),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'))
)

class Paper(db.Model):
    __tablename__ = "past_papers"
    id = db.Column(db.Integer, primary_key=True)
    paper_file = db.Column(db.Text())
    subjects = db.relationship('Subjects', secondary=PaperSubject, backref='papers')

    def __repr__(self):
        return f'{self.paper_file} PAPER' 


class Subjects(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.Text())

    def __repr__(self):
        return self.subject_name
    