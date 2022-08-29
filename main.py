from flask import Flask, render_template, abort, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_ckeditor import CKEditor
from datetime import date, timedelta

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


# update task


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
                flash ("Login successful!", 'user') # flashes a message if successful
                return redirect (url_for("dashboard"))
        flash("Invalid username or password.", 'user')  # redirects user if password entered is wrong
    return render_template ("login.html", form=form)


# route renders signup page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = RegisterForm() # retrieves signup form from forms.py
    if form.validate_on_submit(): 
        existing_username = db.session.query(models.User).filter_by(user_name=form.username.data).first()
        if existing_username is not None: # checks if username is already registered
            flash ("Username already registered.", 'user')
            return render_template ("signup.html", form=form)
        else:
            hashed_password = generate_password_hash(form.password.data, method="sha256") # hashes user password
            new_user = models.User(name=form.name.data, user_name=form.username.data, user_email=form.email.data, user_password=hashed_password) # adds user to database
            db.session.add(new_user)
            db.session.commit() 
            flash ("Sign up successful!", 'user') # flashes a message if successful
            return redirect (url_for("login")) # redirects user to login page if signup is successful
    return render_template ("signup.html", form=form)


# route for user to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash ("Logout successful!", 'user')
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


@app.route("/search_note", methods=('GET', 'POST'))
def search_note():
    if request.method == "POST":
        search_note = request.form.get("search_note")
        #note = db.session.query(models.Notes).filter_by(user=current_user.id, title=search_note).first()
        note = db.session.query(models.Notes).filter_by(user=current_user.id).filter(func.lower(models.Notes.title) == func.lower(search_note)).first()
        if note is None:
            flash ("Note does not exist. Please check for spelling errors.", 'note')
            return redirect ("/notes")
        note_id = note.id
        return redirect ("/note/{}".format(note_id))
    

# route renders specific note page
@app.route("/note/<int:id>")
@login_required
def note(id):
    notes = db.session.query(models.Notes).filter_by(user=current_user.id, id=id)
    folders = db.session.query(models.Folders).filter_by(user=current_user.id)
    return render_template ("note.html", name=current_user.name, notes=notes, folders=folders)


# route for user to change folder of specific note
@app.route("/change_folder/<int:note_id>/<int:folder_id>")
def change_folder(note_id,folder_id):
    current_note = db.session.query(models.Notes).filter_by(id=note_id).first()
    current_note.folder = folder_id
    db.session.commit()
    flash ("Folder successfully changed!", 'note')
    return redirect ("/note/{}".format(note_id))


# route for user to edit note
@app.route("/edit_note/<int:id>", methods=('GET', 'POST'))
def edit_note(id):
    note = db.session.query(models.Notes).filter_by(user=current_user.id, id=id).first()
    form = forms.PostForm()
    note_content = note.content
    form.title.data = note.title
    form.content.data = note_content
    if form.validate_on_submit():
        note.title = request.form.get("title")
        note.content = request.form.get("content")
        db.session.add(note)
        db.session.commit()
        return redirect ("/note/{}".format(id))
    return render_template ("note_edit.html", name=current_user.name, form=form, note=note, note_content=note_content)


@app.route("/delete_note/<int:id>")
def delete_note(id):
    note_delete = db.session.query(models.Notes).filter_by(id=id).first()
    db.session.delete(note_delete)
    db.session.commit()
    return redirect (url_for("notes"))


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
    folders = db.session.query(models.Folders).filter_by(user=current_user.id)
    if request.method == "POST":
        if form.validate_on_submit():
            content = request.form.get("content")
            title = request.form.get("title")
            folder = request.form.get("folder")
            if folder == "None":
                notes = models.Notes(user=current_user.id, title=func.trim(title), content=content)
            elif folder != "None":
                get_folder = db.session.query(models.Folders).filter_by(name=folder).first()
                notes = models.Notes(user=current_user.id, title=func.trim(title), content=content, folder=get_folder.id)
            db.session.add(notes)
            db.session.commit()
            return redirect (url_for("notes"))
    return render_template("new_note.html", name=current_user.name, form=form, folders=folders)


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


@app.route("/update_task/<int:id>")
def update_task(id):
    task = db.session.query(models.Todo).filter_by(id=id).first()
    return render_template ("update_task.html", name=current_user.name)


@app.route("/deadlines")
@login_required
def deadlines():
    deadlines = db.session.query(models.Deadlines).filter_by(user=current_user.id)
    overdue_items = db.session.query(models.Deadlines).filter(models.Deadlines.date < date.today()).all()
    today_items = db.session.query(models.Deadlines).filter(models.Deadlines.date == date.today()).all()
    return render_template ("deadlines.html", name=current_user.name, deadlines=deadlines, overdue_items=overdue_items, today_items=today_items)


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
