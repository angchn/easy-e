from flask import Flask, render_template, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask (__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///student.db"
db = SQLAlchemy(app)

class user(db.model):
    __tablename__ = "user_login"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String())
    user_password = db.Column(db.String())
    todo_id = db.Column(db.Integer, foreign_key=True)
    calender_id = db.Column(db.Integer, foreign_key=True)
    notes_id = db.Column(db.Integer, foreign_key=True)


@app.route("/")
def home():
    return render_template ("home.html", page_title="Home")

if __name__ == "__main__":
    app.run(debug=True)
