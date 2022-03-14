from flask import Flask, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask (__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

import models

@app.route("/")
def home():
    return render_template ("home.html", page_title="Home")

@app.route("/past_papers")
def papers():
    papers = models.Paper.query.all()
    return render_template ("papers.html", page_title="Past_Papers", papers=papers)

@app.route("/past_papers_english")
def english():
    return render_template ("english.html", page_title="English_Past_Papers")

if __name__ == "__main__":
    app.run(debug=True)
