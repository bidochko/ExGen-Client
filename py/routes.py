from app import application
from flask import Flask, render_template, redirect, request, send_from_directory, url_for, session, flash
from functools import wraps

#Password Hashing
from passlib.hash import sha256_crypt
from saltgen import createSalt

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

#Secret key, tbh I don't know what this does but it complains when I dont set one
SECRET_KEY = os.urandom(32)
application.config['SECRET_KEY'] = SECRET_KEY

# Login authentication
def login_required(f):
    @wraps(f) #wrapper
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('index')) #Return to login page
    return wrap

#Logout
@application.route("/logout/")
@login_required
def logout():
    session.clear()
    gc.collect()
    return redirect(url_for('index'))


#Index / Login
@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index():
    error = '' #temp definition
    try:
        conn, trans = connect() #Connect SQLAlchemy Engine to MySQL
        if request.method == "POST": #user presses "login"
            data = conn.execute("SELECT * from User where UserName = %s", thwart(request.form['username']))
            for row in data:
                hash = row[2] # 3rd column is the hashed password
                salt = row[3] # 4th column is the salt

            #'$5$rounds=555000$'+ salt + '$' + hash
            formattedhash = "$5$rounds=555000$" + salt + "$" + hash
            if sha256_crypt.verify(request.form['password'], formattedhash):
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
            randomSalt = createSalt()
            password = sha256_crypt.encrypt((str(form.password.data)), salt=randomSalt, rounds=555000)
            password = password.split("$")[4]

            conn, trans = connect()
            try:
                type = "student"
                conn.execute("INSERT INTO User (UserName, Hash, Salt, Type) VALUES (%s, %s, %s, %s)", (thwart(username), thwart(password), randomSalt, type))
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
@login_required
def home():
    return render_template("studenthome.html")
#Student Exams
@application.route("/exams/", methods=['GET', 'POST'])
@login_required
def exams():
    return render_template("studentexams.html")
#Student Results
@application.route("/results/", methods=['GET', 'POST'])
@login_required
def results():
    return render_template("studentresults.html")
#Student Settings
@application.route("/settings/", methods=['GET', 'POST'])
@login_required
def settings():
    return render_template("studentsettings.html")

@application.route("/hashing/")
@login_required
def hashing():
    slt = "testing"
    hash1 = sha256_crypt.using(salt=slt).hash("password")
    slt2 = "woahman"
    hash2 = sha256_crypt.using(salt=slt2).hash("password")
    return hash2
