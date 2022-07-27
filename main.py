from doctest import NORMALIZE_WHITESPACE
from re import I
from flask import Flask, render_template, abort, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_ckeditor import CKEditor

app = Flask (__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
ckeditor = CKEditor(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

import models
import forms
from forms import LoginForm, RegisterForm


# Flask login (gets user_id)
@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))


# route renders home page
@app.route("/")
def home():
    return render_template ("home.html", page_title="Home")


# route renders login page
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm() # retrieves login form from forms.py
    if form.validate_on_submit(): 
        user = models.User.query.filter_by(user_name=form.username.data).first()
        if user: # checks user input with password hash stored in database
            if check_password_hash(user.user_password, form.password.data):
                login_user(user, remember=form.remember.data)
                flash ("Login successful!", 'login') # flashes a message if successful
                return redirect (url_for("dashboard"))
        return "<h1>Invalid username or password.</h1>" # redirects user if password entered is wrong
    return render_template ("login.html", form=form)


# route renders signup page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = RegisterForm() # retrieves signup form from forms.py
    if form.validate_on_submit(): 
        hashed_password = generate_password_hash(form.password.data, method="sha256") # hashes user password
        new_user = models.User(name=form.name.data, user_name=form.username.data, user_email=form.email.data, user_password=hashed_password) # adds user to database
        db.session.add(new_user)
        db.session.commit() 
        flash ("Sign up successful!", 'login') # flashes a message if successful
        return redirect (url_for("login")) # redirects user to login page if signup is successful
    return render_template ("signup.html", form=form)


# route for user to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect (url_for("home"))


# route renders user dashboard
@app.route("/dashboard")
@login_required
def dashboard():
    incomplete_tasks = models.Todo.query.filter_by(user=current_user.id, complete=False)
    complete_tasks = models.Todo.query.filter_by(user=current_user.id, complete=True)
    notes = models.Notes.query.filter_by(user=current_user.id, favourite=True)
    folders = models.Folders.query.filter_by(user=current_user.id)
    return render_template ("dashboard.html", name=current_user.name, incomplete_tasks=incomplete_tasks, complete_tasks=complete_tasks, notes=notes, folders=folders)


# route renders all notes page
@app.route("/notes")
@login_required
def notes():
    favourite_notes = db.session.query(models.Notes).filter_by(user=current_user.id, favourite=True)
    other_notes = db.session.query(models.Notes).filter_by(user=current_user.id, favourite=False)
    folders = db.session.query(models.Folders).filter_by(user=current_user.id)
    return render_template ("notes.html", name=current_user.name, favourite_notes=favourite_notes, other_notes=other_notes, folders=folders)


# route renders specific note page
@app.route("/note/<int:id>")
@login_required
def note(id):
    notes = db.session.query(models.Notes).filter_by(user=current_user.id, id=id)
    return render_template("note.html", name=current_user.name, notes=notes)


# route for user to add new folder
@app.route("/add_folder", methods=('GET', 'POST'))
def add_folder():
    if request.method == "POST":
        folder_add = request.form.get("folder_add")
        new_folder = models.Folders(name=folder_add, user=current_user.id)
        db.session.add(new_folder)
        db.session.commit()
    return redirect (url_for("notes"))


# route renders specific folder page
@app.route("/folder/<int:id>")
@login_required
def folder(id):
    folders = db.session.query(models.Folders).filter_by(user=current_user.id, id=id)
    notes = db.session.query(models.Notes).filter_by(user=current_user.id, folder=id)
    return render_template ("folder.html", name=current_user.name, notes=notes, folders=folders)


# route renders new note page
@app.route("/new_note", methods=('GET', 'POST'))
def new_note():
    form = forms.PostForm()
    if request.method == "POST":
        if form.validate_on_submit():
            body = request.form.get("body")
            title = request.form.get("title")
            notes = models.Notes(user=current_user.id, name=title, content=body)
            db.session.add(notes)
            db.session.commit()
            return redirect (url_for("notes"))
    return render_template("new_note.html", name=current_user.name, form=form)


# route for user to favourite note
@app.route("/favourite_note/<int:id>")
def favourite_note(id):
    note = db.session.query(models.Notes).filter_by(id=id).first()
    note.favourite = True
    db.session.commit()
    return redirect (url_for("notes"))


# route for user to un-favourite note
@app.route("/unfavourite_note/<int:id>")
def unfavourite_note(id):
    note = db.session.query(models.Notes).filter_by(id=id).first()
    note.favourite = False
    db.session.commit()
    return redirect (url_for("notes"))


# route for user to add todo task
@app.route("/add_task", methods=('GET', 'POST'))
def add_task():
    if request.method == "POST":
        task_add = request.form.get("task_add")
        new_task = models.Todo(name=task_add, user=current_user.id)
        db.session.add(new_task)
        db.session.commit()
    return redirect (url_for("dashboard"))


# route for user to delete task
@app.route("/delete_task/<int:id>")
def delete_task(id):
    task_delete = db.session.query(models.Todo).filter_by(id=id).first()
    db.session.delete(task_delete)
    db.session.commit()
    return redirect (url_for("dashboard"))


# route for user to mark task complete
@app.route("/complete_task/<int:id>")
def complete_task(id):
    task = db.session.query(models.Todo).filter_by(id=id).first()
    task.complete = True
    db.session.commit()
    return redirect (url_for("dashboard"))


# route for user to un-mark task complete
@app.route("/redo_complete_task/<int:id>")
def redo_complete_task(id):
    task = db.session.query(models.Todo).filter_by(id=id).first()
    task.complete = False
    db.session.commit()
    return redirect (url_for("dashboard"))


# route renders past papers page
@app.route("/past_papers")
def papers():
    papers = models.Paper.query.all()
    return render_template ("papers.html", page_title="Past_Papers", papers=papers)

# route renders 
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
