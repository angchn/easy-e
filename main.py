from re import I
from flask import Flask, render_template, abort, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask (__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

import models

class LoginForm(FlaskForm):
    username = StringField("username", validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField("password", validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField("remember me")

class RegisterForm(FlaskForm):
    email = StringField("email", validators=[InputRequired(), Email(message="Invalid email"), Length(max=50)])
    username = StringField("username", validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField("password", validators=[InputRequired(), Length(min=8, max=80)])

@app.route("/")
def home():
    return render_template ("home.html", page_title="Home")

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit(): 
        user = models.User.query.filter_by(user_name=form.username.data).first()
        if user:
            if check_password_hash(user.user_password, form.password.data):
                return redirect (url_for("dashboard"))
        return "<h1>Invalid username or password.</h1>"
    return render_template("login.html", form=form)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = RegisterForm()
    if form.validate_on_submit(): 
        hashed_password = generate_password_hash(form.password.data, method="sha256")
        new_user = models.User(user_name=form.username.data, user_email=form.email.data, user_password=form.password.data)
        db.session.add(new_user)
        db.session.commit
        return "<h1>New user has been created!</h1>"
    return render_template("signup.html", form=form)

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/past_papers")
def papers():
    papers = models.Paper.query.all()
    return render_template ("papers.html", page_title="Past_Papers", papers=papers)

@app.route("/past_papers_english")
def english():
    epapers = models.Paper.query.filter_by(subject=1)
    return render_template ("english.html", page_title="English_Past_Papers", epapers=epapers)

@app.route("/past_papers_math")
def maths():
    mpapers = models.Paper.query.filter_by(subject=2)
    return render_template("maths.html", page_title="Math_Past_Papers", mpapers=mpapers)

@app.route("/past_papers_physics")
def physics():
    return render_template("physics.html", page_title="Physics_Past_Papers")

@app.route("/past_papers_chemistry")
def chemistry():
    return render_template("chemistry.html", page_title="Chemistry_Past_Papers")

@app.route ("/past_papers_biology")
def biology():
    return render_template("biology.html", page_title="Biology_Past_Papers")

if __name__ == "__main__":
    app.run(debug=True)
