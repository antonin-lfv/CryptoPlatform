from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user
from models import User
from app import db

BLP_auth = Blueprint('BLP_auth', __name__,
                     template_folder='templates',
                     static_folder='static')


@BLP_auth.route('/')
@BLP_auth.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        print(request.form)
        if (username := request.form.get("login_username")) and (password := request.form.get("login_password")):
            user = User.query.filter_by(username=username).first()
            # if user already exists
            if not user or not check_password_hash(user.password, password):
                return render_template('auth/auth_login.html', wrong_credentials=True)
            login_user(user)
            return redirect(url_for('BLP_general.home'))
    return render_template('auth/auth_login.html', wrong_credentials=False)


@BLP_auth.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if (email := request.form.get("signup_email")) and (password := request.form.get("signup_password")) and (
                username := request.form.get("signup_username")):
            user = User.query.filter_by(email=email).first()
            # if user already exists
            if user:
                return render_template('auth/auth_register.html', already_exists=True)
            # else - creation of the user
            new_user = User()
            new_user.email = email
            new_user.username = username
            new_user.password = generate_password_hash(password, method='scrypt')
            # add the new user to the database
            db.session.add(new_user)
            db.session.commit()
            flash('You have been successfully registered', 'success')
            return render_template('auth/auth_login.html', wrong_credentials=False)
    return render_template('auth/auth_register.html', already_exists=False)


@BLP_auth.route('/logout', methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for('BLP_auth.login'))
