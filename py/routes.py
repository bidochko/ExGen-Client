from app import application
from flask import Flask, render_template, redirect, request, send_from_directory, url_for, session, flash

#Password Hashing
from passlib.hash import sha256_crypt

#Flask Form
from flask_wtf import FlaskForm
from wtforms import Form, validators, TextField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

#SQL Injection prevention
from MySQLdb import escape_string as thwart
from dbconnect import connect

#Garbace collection and OS
import gc
import os

SECRET_KEY = os.urandom(32)
application.config['SECRET_KEY'] = SECRET_KEY

#Index / Login
@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index():
    error = ''
    try:
        conn, trans = connect()
        if request.method == "POST":
            data = conn.execute("SELECT * from User where UserName = %s", thwart(request.form['username']))
            for row in data:
                hash = row[2]
            if sha256_crypt.using(salt="hahamemelol").verify(request.form['password'], hash):
                session['logged_in'] = True
                session['username'] = request.form['username']
                return redirect(url_for("home"))
            else:
                error = "Incorrect credentials"
        gc.collect()
        conn.close()
        return render_template("login.html", error=error)
    except Exception as e:
        error = "Incorrect credentials"
        return render_template("login.html", error = error)

#Register
class RegistrationForm(Form):
    name = TextField("Full Name", [validators.Length(min=1, max=128)])
    username = TextField("Email", [validators.Length(min=1, max=128)])
    password = PasswordField("Password", [validators.Required(), validators.Length(min=8, max=128), validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Re-enter password')
    accept_tos = BooleanField('I accept giving away my soul', [validators.Required()])

@application.route('/register/', methods=["GET","POST"])
def register():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            name = form.name.data
            username = form.username.data
            slt = "hahamemelol"
            password = sha256_crypt.using(salt=slt).hash((str(form.password.data)))

            conn, trans = connect()
            try:
                type = "student"
                conn.execute("INSERT INTO User (UserName, Hash, Salt, Type) VALUES (%s, %s, %s, %s)", (thwart(username), thwart(password), slt, type))
                trans.commit()  # transaction is not committed yet
            except:
                trans.rollback() # this rolls back the transaction unconditionally

            flash("Thanks for Registering!")
            conn.close()
            gc.collect()

            session['logged_in'] = True
            session['username'] = username

            return redirect(url_for('index'))
        return render_template("register.html", form=form)

    except Exception as e:
        return(str(e))

#Cookies
@application.route("/cookies/", methods=['GET', 'POST'])
def cookies():
    return render_template("cookies.html")
#Student Home
@application.route("/home/", methods=['GET', 'POST'])
def home():
    return render_template("studenthome.html")
#Student Exams
@application.route("/exams/", methods=['GET', 'POST'])
def exams():
    return render_template("studentexams.html")
#Student Results
@application.route("/results/", methods=['GET', 'POST'])
def results():
    return render_template("studentresults.html")
#Student Settings
@application.route("/settings/", methods=['GET', 'POST'])
def settings():
    return render_template("studentsettings.html")

@application.route("/hashing/")
def hashing():
    slt = "testing"
    hash = sha256_crypt.using(salt=slt).hash("password")
    return hash
