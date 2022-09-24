from main import db
from flask_login import UserMixin


DeadlineTag = db.Table(
    "deadline_tag",
    db.Column("deadline_id", db.Integer, db.ForeignKey("deadline.id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id")),
)


class Deadline(db.Model):
    __tablename__ = "deadline"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey("user_login.id"))
    date = db.Column(db.Date)
    name = db.Column(db.String())

    tags = db.relationship("Tag", secondary=DeadlineTag, back_populates="deadlines")

    def __repr__(self):
        return self.name


class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey("user_login.id"))
    name = db.Column(db.String())

    deadlines = db.relationship(
        "Deadline", secondary=DeadlineTag, back_populates="tags"
    )

    def __repr__(self):
        return self.name


class Paper(db.Model):
    __tablename__ = "past_papers"
    id = db.Column(db.Integer, primary_key=True)
    paper_file = db.Column(db.Text())
    name = db.Column(db.Text())
    subject = db.Column(db.Integer, db.ForeignKey("subjects.id"))
    standard = db.Column(db.Text())

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

    todo = db.relationship("Todo", backref="todo")


class Todo(db.Model):
    __tablename__ = "todo"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    user = db.Column(db.Integer(), db.ForeignKey("user_login.id"))
    complete = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return self.name


class Folders(db.Model):
    __tablename__ = "folders"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer(), db.ForeignKey("user_login.id"))
    name = db.Column(db.String(50))

    def __repr__(self):
        return self.name


class Notes(db.Model):
    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer(), db.ForeignKey("user_login.id"))
    title = db.Column(db.String(50))
    favourite = db.Column(db.Boolean, default=False)
    folder = db.Column(db.Integer, db.ForeignKey("folders.id"))
    content = db.Column(db.String())

    folder_name = db.relationship("Folders", backref="folder")

    def __repr__(self):
        return self.name
