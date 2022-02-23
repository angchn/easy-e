from flask import Flask, render_template, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask (__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///student.db"
db = SQLAlchemy(app)




@app.route("/")
def home():
    return render_template ("home.html", page_title="Home")

if __name__ == "__main__":
    app.run(debug=True)
