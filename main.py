from datetime import date, datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from flask_ckeditor import CKEditor
from config import Config


import models
import forms
from forms import LoginForm, RegisterForm


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

ckeditor = CKEditor(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# feature incomplete due to time constraints, pep 8, testing (web, routes, database), footer links,
# (expected and then what i got - test queries), look at HCI (CS FIELDGUIDE)


@login_manager.user_loader
def load_user(user_id):
    """Gets user information from database."""
    return models.User.query.get(int(user_id))


@app.route("/")
def home():
    """Route for home page."""
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Route for user to login."""
    form = LoginForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(user_name=form.username.data).first()

        if user:  # Checks if user password matches hash stored in database.
            if check_password_hash(user.user_password, form.password.data):
                login_user(user, remember=form.remember.data)
                flash("Login successful!", "user")
                return redirect(url_for("dashboard"))

        elif (
            user is None
        ):  # If user password does not match, flash error message and redirect.
            flash("Invalid username or password.", "user")
            return redirect("/login")

    return render_template("login.html", form=form)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Route for user to signup."""
    form = RegisterForm()
    if form.validate_on_submit():
        # Searches database for username.
        existing_username = (
            db.session.query(models.User)
            .filter_by(user_name=form.username.data)
            .first()
        )
        existing_email = (
            db.session.query(models.User)
            .filter_by(user_email=form.email.data)
            .first()
        )

        # If username or email is already registered, flash message and redirect.
        if existing_username is not None:
            flash("Username already registered.", "user")
            return render_template("signup.html", form=form)
        elif existing_email is not None:
            flash("Email already registered.", "user")
            return render_template("signup.html", form=form)

        # If username does not already exist, generate password hash and add new user to database.
        else:
            hashed_password = generate_password_hash(
                form.password.data, method="sha256"
            )
            new_user = models.User(
                name=form.name.data,
                user_name=form.username.data,
                user_email=form.email.data,
                user_password=hashed_password,
            )
            db.session.add(new_user)
            db.session.commit()
            flash(
                "Sign up successful!", "user"
            )  # Flash message if user is successfully added.
            return redirect(url_for("login"))

    return render_template("signup.html", form=form)


@app.route("/logout")
@login_required
def logout():
    """Logs out current user."""
    logout_user()
    flash("Logout successful!", "user")
    return redirect(url_for("home"))


@app.route("/dashboard")
@login_required
def dashboard():
    """Route renders user's dashboard."""
    incomplete_tasks = models.Todo.query.filter_by(user=current_user.id, complete=False)
    complete_tasks = models.Todo.query.filter_by(user=current_user.id, complete=True)
    notes = models.Notes.query.filter_by(user=current_user.id, favourite=True)
    folders = models.Folders.query.filter_by(user=current_user.id)

    # Filters user deadlines based on today date.
    today_items = (
        db.session.query(models.Deadline)
        .filter(models.Deadline.date == date.today()).filter_by(user=current_user.id)
        .all()
    )
    later_items = (
        db.session.query(models.Deadline)
        .filter(models.Deadline.date > date.today()).filter_by(user=current_user.id)
        .all()
    )
    return render_template(
        "dashboard.html",
        name=current_user.name,
        incomplete_tasks=incomplete_tasks,
        complete_tasks=complete_tasks,
        notes=notes,
        folders=folders,
        today_items=today_items,
        later_items=later_items,
    )


@app.route("/notes")
@login_required
def notes():
    """Route renders user's notes page."""
    # Filters notes based on favourited and non-favourited.
    favourite_notes = db.session.query(models.Notes).filter_by(
        user=current_user.id, favourite=True
    )
    other_notes = db.session.query(models.Notes).filter_by(
        user=current_user.id, favourite=False
    )

    folders = db.session.query(models.Folders).filter_by(user=current_user.id)

    return render_template(
        "notes.html",
        name=current_user.name,
        favourite_notes=favourite_notes,
        other_notes=other_notes,
        folders=folders,
    )


@app.route("/search_note", methods=("GET", "POST"))
def search_note():
    """Route for user to search their notes."""
    if request.method == "POST":
        search_note = request.form.get("search_note")  # Gets user's input.
        note = (
            db.session.query(models.Notes)
            .filter_by(user=current_user.id)
            .filter(
                func.lower(models.Notes.title) == func.lower(search_note)
            )  # Makes user input non-case-sensitive.
            .first()
        )

        if note is None:  # Flash message if search returns none.
            flash("Note does not exist. Please check for spelling errors.", "note")
            return redirect("/notes")

        note_id = note.id  # Gets id of note from user search, if search is successful.
        return redirect("/note/{}".format(note_id))


# route renders specific note page
@app.route("/note/<int:id>")
@login_required
def note(id):
    """Route that renders each individual note."""
    note = (  # Gets note from database.
        db.session.query(models.Notes)
        .filter_by(user=current_user.id, id=id)
        .first_or_404()
    )
    folders = db.session.query(models.Folders).filter_by(
        user=current_user.id
    )  # Gets folders from database.
    return render_template(
        "note.html", name=current_user.name, note=note, folders=folders
    )


@app.route("/change_folder/<int:note_id>/<int:folder_id>")
def change_folder(note_id, folder_id):
    """Route for user to change folder of a note."""
    current_note = (
        db.session.query(models.Notes).filter_by(id=note_id).first_or_404()
    )  # Gets current note from database.
    current_note.folder = folder_id  # Changes folder of current note to new folder.
    db.session.commit()
    flash("Folder successfully changed!", "note")
    return redirect("/note/{}".format(note_id))


@app.route("/edit_note/<int:id>", methods=("GET", "POST"))
def edit_note(id):
    """Route for user to edit individual notes."""
    note = (  # Gets note from database.
        db.session.query(models.Notes)
        .filter_by(user=current_user.id, id=id)
        .first_or_404()
    )
    # Gets form and populates form with existing data from database.
    form = forms.PostForm()
    note_content = note.content
    form.title.data = note.title
    form.content.data = note_content

    if form.validate_on_submit():
        # Updates database with new user input.
        note.title = request.form.get("title")
        note.content = request.form.get("content")
        db.session.add(note)
        db.session.commit()
        return redirect("/note/{}".format(id))

    return render_template(
        "note_edit.html",
        name=current_user.name,
        form=form,
        note=note,
        note_content=note_content,
    )


@app.route("/delete_note/<int:id>")
def delete_note(id):
    """Route for user to delete note."""
    note_delete = (
        db.session.query(models.Notes).filter_by(id=id).first_or_404()
    )  # Gets note from database.
    db.session.delete(note_delete)
    db.session.commit()
    return redirect(url_for("notes"))


@app.route("/add_folder", methods=("GET", "POST"))
def add_folder():
    """Route for user to add new folder."""
    if request.method == "POST":
        folder_add = request.form.get("folder_add")  # Gets user input.
        new_folder = models.Folders(name=folder_add, user=current_user.id)
        db.session.add(new_folder)
        db.session.commit()
    return redirect(url_for("notes"))


@app.route("/folder/<int:id>")
@login_required
def folder(id):
    """Route for user to see all notes in each folder."""
    folders = db.session.query(models.Folders).filter_by(user=current_user.id, id=id)
    notes = db.session.query(models.Notes).filter_by(user=current_user.id, folder=id)
    return render_template(
        "folder.html", name=current_user.name, notes=notes, folders=folders
    )


@app.route("/new_note", methods=("GET", "POST"))
def new_note():
    """Route for user to add new note."""
    form = forms.PostForm()  # Gets form.
    folders = db.session.query(models.Folders).filter_by(user=current_user.id)

    if request.method == "POST":
        if form.validate_on_submit():
            content = request.form.get("content")
            title = request.form.get("title")
            folder = request.form.get("folder")

            if (
                folder == "None"
            ):  # If user does not assign a folder to the note, add note regardless.
                notes = models.Notes(
                    user=current_user.id, title=func.trim(title), content=content
                )

            elif (
                folder != "None"
            ):  # If user assigns a folder to note, get folder and then add note.
                get_folder = (
                    db.session.query(models.Folders).filter_by(name=folder).first()
                )
                notes = models.Notes(
                    user=current_user.id,
                    title=func.trim(title),
                    content=content,
                    folder=get_folder.id,
                )

            db.session.add(notes)
            db.session.commit()
            return redirect(url_for("notes"))
    return render_template(
        "new_note.html", name=current_user.name, form=form, folders=folders
    )


@app.route("/favourite_note/<int:id>")
def favourite_note(id):
    """Route for user to favourite note."""
    note = db.session.query(models.Notes).filter_by(id=id).first_or_404()
    note.favourite = True  # Sets BooleanField to True.
    db.session.commit()
    return redirect(url_for("notes"))


@app.route("/unfavourite_note/<int:id>")
def unfavourite_note(id):
    """Route for user to unfavourite note."""
    note = db.session.query(models.Notes).filter_by(id=id).first_or_404()
    note.favourite = False  # Sets BooleanField to False.
    db.session.commit()
    return redirect(url_for("notes"))


@app.route("/add_task", methods=("GET", "POST"))
def add_task():
    """Route for user to add new task."""
    if request.method == "POST":
        task_add = request.form.get("task_add")  # Gets user input.
        new_task = models.Todo(name=task_add, user=current_user.id)
        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for("dashboard"))


@app.route("/delete_task/<int:id>")
def delete_task(id):
    """Route for user to delete task."""
    task_delete = db.session.query(models.Todo).filter_by(id=id).first_or_404()
    db.session.delete(task_delete)
    db.session.commit()
    return redirect(url_for("dashboard"))


@app.route("/complete_task/<int:id>")
def complete_task(id):
    """Route for user to mark task as complete."""
    task = db.session.query(models.Todo).filter_by(id=id).first_or_404()
    task.complete = True  # Sets BooleanField to True.
    db.session.commit()
    return redirect(url_for("dashboard"))


@app.route("/redo_complete_task/<int:id>")
def redo_complete_task(id):
    """Route for user to un-complete task."""
    task = db.session.query(models.Todo).filter_by(id=id).first_or_404()
    task.complete = False  # Sets BooleanField to False.
    db.session.commit()
    return redirect(url_for("dashboard"))


@app.route("/deadlines")
@login_required
def deadlines():
    """Route renders user's deadlines."""
    overdue_items = (  # Filters deadlines that are overdue.
        db.session.query(models.Deadline)
        .filter(models.Deadline.date < date.today()).filter_by(user=current_user.id)
        .all()
    )
    today_items = (  # Filters deadlines due today.
        db.session.query(models.Deadline)
        .filter(models.Deadline.date == date.today()).filter_by(user=current_user.id)
        .all()
    )
    later_items = (  # Filters deadlines due in the future.
        db.session.query(models.Deadline)
        .filter(models.Deadline.date > date.today()).filter_by(user=current_user.id)
        .all()
    )
    return render_template(
        "deadlines.html",
        name=current_user.name,
        overdue_items=overdue_items,
        today_items=today_items,
        later_items=later_items,
    )


@app.route("/new_deadline", methods=("GET", "POST"))
def new_deadline():
    """Route for user to add new deadline. (Feature not complete due to time constraints.)"""
    form = forms.DeadlineForm()
    if request.method == "POST":

        if form.validate_on_submit():
            name = request.form.get("name")
            date = datetime.strptime(form.date.data, "%Y-%m-%d")
            new_deadline = models.Deadline(user=current_user.id, name=name, date=date)
            db.session.add(new_deadline)
            db.session.commit()
        return redirect(url_for("deadlines"))

    return render_template("deadline_new.html", name=current_user.name, form=form)


@app.route("/past_papers_english")
def english():
    """Route renders page for all past English papers."""
    epapers = models.Paper.query.filter_by(subject=1)
    return render_template(
        "english.html", page_title="English_Past_Papers", epapers=epapers
    )


@app.route("/past_papers_math")
def maths():
    """Route renders page for all past Maths papers."""
    mpapers = models.Paper.query.filter_by(subject=2)
    return render_template("maths.html", page_title="Math_Past_Papers", mpapers=mpapers)


@app.route("/page_unavailable")
def page_unavailable():
    """Route redirects user to empty page, as feature is unavailable due to time constraints."""
    return render_template("page_unavailable.html")


@app.errorhandler(404)
def page_not_found(e):
    """Error page."""
    return render_template("404.html")


if __name__ == "__main__":
    app.run(debug=True)
