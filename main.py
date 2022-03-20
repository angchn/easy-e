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
    epapers = models.Paper.query.filter_by(subject=1)
    return render_template ("english.html", page_title="English_Past_Papers", epapers=epapers)

@app.route("/past_papers_math")
def math():
    epapers = models.Paper.query.filter_by(subject=1)
    return render_template("math.html", page_title="Math_Past_Papers")

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
