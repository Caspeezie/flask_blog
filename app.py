from enum import unique
from logging import debug
from flask import Flask, render_template, request, session
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
import os

from werkzeug.utils import redirect


app = Flask(__name__)
app.secret_key = '88440430ec3ee1ddcaafb43d3c3f76'
# finding the current app path. (Location of this file)
project_dir = os.path.dirname(os.path.abspath(__file__))

# creating a database file (bookdatabase.db) in the above found path.
database_file = "sqlite:///{}".format(os.path.join(project_dir, "blogposts.db"))

# connecting the database file (bookdatabase.db) to the sqlalchemy dependency.
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# connecting this app.py file to the sqlalchemy
db = SQLAlchemy(app)

class Posts(db.Model):
    title = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    content = db.Column(db.String(700), unique=False, nullable=False)

    def __repr__(self):
        return f"Title: {self.title}"

class User(db.Model):
    username = db.Column(db.String(20), unique=True, nullable=False, primary_key=True)
    password = db.Column(db.String(50), unique=False, nullable=False)

    def __repr__(self):
        return f"Username: {self.username}"   



@app.route('/')
def home():
    posts = Posts.query.all()

    return render_template("index.html", posts = posts)

@app.route('/newpost', methods=["GET", "POST"])
def newpost():
    if 'user' in session:
        if request.form:
            title = request.form.get('title')
            content = request.form.get('content')
            post = Posts(title=title, content=content)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('home'))

        return render_template("newpost.html")
    else:
        return redirect(url_for('login'))

@app.route('/confirm/<title>')
def confirm(title):
    if 'user' in session:
        selected_post = Posts.query.filter_by(title=title).first()
        return render_template("confirm.html", selected_post=selected_post)
    else:
        return redirect(url_for('login'))


@app.route('/delete/<title>', methods=["GET", "POST"])
def delete(title):
    if 'user' in session:
        post = Posts.query.filter_by(title=title).first()
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


@app.route('/edit/<title>', methods=["POST", "GET"])
def edit(title):
    if 'user' in session:
        selected_post = Posts.query.filter_by(title=title).first()
        if request.form:
            selected_post.title = request.form.get('title')
            selected_post.content = request.form.get('content')
            db.session.commit()
            return redirect(url_for('home'))
        return render_template("edit.html", selected_post=selected_post)
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        users = User.query.all()

        for user in users:
            if username == user.username and password == user.password:
                session['user'] = user.username
                return redirect(url_for('home'))
            else:
                return render_template('login.html')
            
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)