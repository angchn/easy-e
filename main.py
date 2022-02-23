from flask import Flask, render_template, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask (__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///pizza.db"
db = SQLAlchemy(app)
