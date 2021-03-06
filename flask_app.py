# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import login_user, LoginManager, UserMixin, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__)
app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="jamwardy",
    password="dataTings!",
    hostname="jamwardy.mysql.pythonanywhere-services.com",
    databasename="jamwardy$comments",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.secret_key = "FMvbzG8n1uZSB2YZK6Kb"
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.username

class Comment(db.Model):

    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(4096))
    posted = db.Column(db.DateTime, default=datetime.now)

    commenter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    commenter = db.relationship('User', foreign_keys=commenter_id)

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username = user_id).first()

@app.route('/', methods = ["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_page.html", comments = Comment.query.all())

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    comment = Comment(content = request.form["contents"], commenter = current_user)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login/', methods = ["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login_page.html", error = False)

    user = load_user(request.form["username"])
    if user is None:
        return render_template("login_page.html", error=True)

    if not user.check_password(request.form["password"]):
        return render_template("login_page.html", error = True)

    login_user(user)
    return redirect(url_for('index'))

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/new_user/", methods = ["GET", "POST"])
def new_user():
    if request.method == "GET":
        return render_template("new_user.html", error = False)

    new_username = request.form["username"]
    if load_user(new_username) is not None:
        return render_template("new_user.html", error=True)

    new_password_hash = generate_password_hash(request.form["password"])
    new_user_object = User(username = new_username, password_hash = new_password_hash)
    db.session.add(new_user_object)
    db.session.commit()

    user = load_user(new_username)
    login_user(user)
    return redirect(url_for('index'))