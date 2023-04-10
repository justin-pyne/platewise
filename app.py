from flask import Flask, flash, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
import os
import re

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Backend validation
        if len(username) < 3 or len(username) > 20:
            flash("Username must be between 3 and 20 characters long.", "danger")
            return render_template("register.html")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email address.", "danger")
            return render_template("register.html")
        if len(password) < 6 or len(password) > 60:
            flash("Password must be between 6 and 60 characters long.", "danger")
            return render_template("register.html")

        # Check for existing user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "danger")
            return render_template("register.html")

        # Check for existing email
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("Email address already exists. Please choose a different one.", "danger")
            return render_template("register.html")

        # Save the user to the database
        password_hash = generate_password_hash(password)
        new_user = User(username=username, email=email, password=password_hash)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")
    
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("profile"))

        flash("Invalid email or password")
    return render_template("login.html")
    
@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)
    
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)