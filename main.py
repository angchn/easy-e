from re import I
from flask import Flask, render_template, abort, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask (__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

import models
from forms import LoginForm, RegisterForm

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))

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
                login_user(user, remember=form.remember.data)
                flash ("Login successful!", 'login')
                return redirect (url_for("dashboard"))
        return "<h1>Invalid username or password.</h1>"
    return render_template ("login.html", form=form)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = RegisterForm()
    if form.validate_on_submit(): 
        hashed_password = generate_password_hash(form.password.data, method="sha256")
        new_user = models.User(name=form.name.data, user_name=form.username.data, user_email=form.email.data, user_password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash ("Sign up successful!", 'login')
        return redirect (url_for("login"))
    return render_template ("signup.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect (url_for("home"))

@app.route("/dashboard")
@login_required
def dashboard():
    tasks = models.Todo.query.filter_by(user=current_user.id)
    return render_template ("dashboard.html", name=current_user.name, tasks=tasks)

@app.route("/add_task", methods=('GET', 'POST'))
def add_task():
    if request.method == "POST":
        task_add = request.form.get("task_add")
        new_task = models.Todo(name=task_add, user=current_user.id)
        db.session.add(new_task)
        db.session.commit()
    return redirect (url_for("dashboard"))

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
