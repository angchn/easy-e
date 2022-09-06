from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, DateField, SelectMultipleField
from wtforms.validators import InputRequired, Email, Length, DataRequired
from flask_ckeditor import CKEditorField
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    username = StringField("username", validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField("password", validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField("remember me")

class RegisterForm(FlaskForm):
    name = StringField("name", validators=[InputRequired(), Length(min=2)])
    email = StringField("email", validators=[InputRequired(), Email(message="Invalid email"), Length(max=50)])
    username = StringField("username", validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField("password", validators=[InputRequired(), Length(min=8, max=80)])

class PostForm(FlaskForm):
    title = StringField("title", validators=[DataRequired(), Length(min=2)])
    content = CKEditorField("content", validators=[DataRequired()], widget=TextArea())

class DeadlineForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    date = DateField("date", format="%Y-%m-%d", validators=[DataRequired()])
    #tags = SelectMultipleField("tags", coerce=int)
    