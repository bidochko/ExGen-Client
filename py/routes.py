from app import application
from flask import Flask, render_template, redirect, request, send_from_directory, url_for, session, flash, jsonify
from functools import wraps

#Password Hashing
from passlib.hash import sha256_crypt
from saltgen import createSalt

#Flask Form
from flask_wtf import FlaskForm
from wtforms import Form, validators, TextField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

#SQL Injection prevention
from MySQLdb import escape_string as thwart
from db import database
from dbconnect import connect

#Emailing
from emailsetup import sendMessage

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

# Logged out requirenment -> cant log in when already logged in
def logout_required(f):
    @wraps(f) #wrapper
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return redirect(url_for('home')) #Return to login page
        else:
            return f(*args, **kwargs)
    return wrap

#Logout
@application.route("/logout/")
@login_required
def logout():
    session.clear() #clear session info
    gc.collect() #garbage collector
    return redirect(url_for('index')) #return user to index

#Index / Login
@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
@logout_required
def index():
    error = "" #temp definition
    if request.method == "POST": #user presses "login"
        user = database.get_user_given_user_name(thwart(request.form['username']))
        if(user == None):
            error = "Incorrect credentials"
            return render_template("login.html", error = error) #refresh with error
        else:
            userid = user.UserID
            email = user.UserName
            hash = user.Hash
            salt = user.Salt
            formattedhash = "$5$rounds=555000$" + salt + "$" + hash #formatted password for .verify function
            if sha256_crypt.verify(request.form['password'], formattedhash):
                session['logged_in'] = True #set session as logged in
                session['username'] = email #set username as email
                session['userid'] = userid #userid
                usertype = "student"
                student = database.get_student_given_user_id(userid)
                if student == None:
                    usertype = "professor"
                elif student.isCourseRep == 1:
                    usertype = "courserep"
                session['usertype'] = usertype #user type i.e. student
                if(usertype == "professor"):
                    professor = database.get_professor_given_user_id(userid)
                    session['professorid'] = professor.ProfessorID
                else:
                    student = database.get_student_given_user_id(userid)
                    session['studentid'] = student.StudentID
                return redirect(url_for('home'))
            else:
                error = "Incorrect credentials"
        return render_template("login.html", error=error)
    return render_template("login.html", error = error) #refresh with error

#Register Form
class RegistrationForm(Form):
    name = TextField("Full Name", [validators.Required(), validators.Length(min=1, max=128)])
    username = TextField("Email", [validators.Required(), validators.Length(min=1, max=128)])
    studentid = TextField("Email", [validators.Required(), validators.Length(min=9, max=9)])
    password = PasswordField("Password", [validators.Required(), validators.Length(min=8, max=128), validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Re-enter password')
    accept_tos = BooleanField('I accept to the use of cookies', [validators.Required()])

@application.route('/register/', methods=["GET","POST"])
@logout_required
def register():
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        studentid = form.studentid.data
        randomSalt = createSalt()
        password = sha256_crypt.encrypt((str(form.password.data)), salt=randomSalt, rounds=555000)
        password = password.split("$")[4]

        user = database.get_user_given_user_name(thwart(username))
        if(user != None):
            flash("Email is already registered")
            return render_template('register.html', form=form)
        else:
            database.create_professor(thwart(username), thwart(password), randomSalt, name, "", thwart(studentid))
        return redirect(url_for('index'))
    return render_template("register.html", form=form)

#Cookies
@application.route("/cookies/", methods=['GET', 'POST'])
def cookies():
    return render_template("cookies.html")

#Redirect 404
@application.errorhandler(404)
def handle_404(e):
    return redirect(url_for('index'))


#Home
@application.route("/home/", methods=['GET', 'POST'])
@login_required
def home():
    if(session['usertype'] == "student"): #Student Home
        module_list = database.get_modules_list_given_student_id(session['studentid'])
        return render_template("student/student-home.html", modules=module_list)
    elif(session['usertype'] == "courserep"): #Course Rep home
        module_list = database.get_modules_list_given_student_id(session['studentid'])
        return render_template("courserep/courserep-home.html", modules=module_list)
    elif(session['usertype'] == "professor"): #Professor home
        #Slight difference with professors as we get the modules that they have created
        professor_modules = database.get_modules_list_given_professor_id(session['professorid'])
        return render_template("professor/professor-home.html", modules=professor_modules)
    elif(session['usertype'] == "admin"): #Admin home
        module_list = database.get_modules_list_given_student_id(session['studentid'])
        return render_template("admin/admin-home.html", modules=module_list)
    else: #temp redirect for other user
        return redirect(url_for('logout'))




#Modules page
#Form for the buttons
class ModuleFormStudent(Form):
    #variable names used in html
    opt_in_course_code = TextField("")
    opt_out_course_code = TextField("")
class ModuleFormProfessor(Form):
    #variable names used in html
    course_code = TextField("")
@application.route("/modules/", methods=['GET', 'POST'])
@login_required
def modules():
    module_code_post = "NULL"
    if(session['usertype'] == "professor"): #professor
        form = ModuleFormProfessor(request.form)
        if request.method == "POST":
            if 'course_code' in request.form: #Deleting a module
                module_code = form.course_code.data
                modules_all = database.get_all_available_modules()
                for module in modules_all:                #Getting module_id from COMPXXX
                    if module.ModuleCode == module_code:
                        module_id = module.ModuleID
                database.delete_module(module_id)
                database.delete_all_students_from_module(module_id)
                database.delete_all_professors_from_module(module_id)
            if 'module_buttons' in request.form: #check if button was pressed
                module_code_post = request.form.get("module_buttons")
    else: #every other user
        form = ModuleFormStudent(request.form)               #Form for the opt-in/out buttons
        if request.method == "POST":     #if button is pressed
            modules_all = database.get_all_available_modules()
            if 'opt_out_course_code' in request.form:        #Opt-out button was pressed
                module_code = form.opt_out_course_code.data  #Get module button id
                for row in modules_all:                #Getting module_id from COMPXXX
                    if row.ModuleCode == module_code:
                        module_id_delete = row.ModuleID
                database.delete_one_student_from_module(session['studentid'], module_id_delete)
            elif 'opt_in_course_code' in request.form:
                module_code = form.opt_in_course_code.data #same as above but for opt-in
                for row in modules_all:
                    if row.ModuleCode == module_code:
                        module_id_add = row.ModuleID
                database.add_student_to_module(session['studentid'], module_id_add, 0)

    #Get registered modules and available modules
    if(session['usertype'] == "student"):
        modules_registerd = database.get_modules_list_given_student_id(session['studentid'])
        modules_available = database.get_available_modules_given_student_id(session['studentid'])
        return render_template("student/student-module.html", modules_registerd=modules_registerd, modules_available=modules_available)
    elif(session['usertype'] == "courserep"): #Course Rep home
        modules_reg = database.get_full_module_list_from_student_id(session['studentid'])
        modules_available = database.get_available_modules_student(session['studentid'])
        return render_template("courserep/courserep-module.html", modules_reg=modules_reg, modules_available=modules_available)
    elif(session['usertype'] == "professor"): #Professor home
        modules_reg = database.get_modules_list_given_professor_id(session['professorid'])
        if module_code_post == "NULL":
            if modules_reg != []:
                module_code_post = modules_reg[0].ModuleCode
        professors = database.get_user_from_professors(module_code_post)
        professors_list = []
        for professor in professors:
            if professor.UserID != session['userid']:
                professors_list.extend([professor])
        return render_template("professor/professor-module.html", modules_reg=modules_reg, module_code_post=module_code_post, professors_list=professors_list)
    elif(session['usertype'] == "admin"): #Admin home
        modules_reg = database.get_full_module_list_from_student_id(session['studentid'])
        modules_available = database.get_available_modules_student(session['studentid'])
        return render_template("admin/admin-module.html", modules_reg=modules_reg, modules_available=modules_available)
    else:
        return redirect(url_for('logout'))

#Professor create exam
class NewModule(Form):
    #variable names used in html
    module_code = TextField("")
    module_name = TextField("")
    module_desc = TextField("")
@application.route("/create-module/", methods=['GET', 'POST'])
@login_required
def create_module():
    if(session['usertype'] == "professor"): #professors
        conn, trans = connect()
        form = NewModule(request.form)
        if request.method == "POST" and form.validate(): #on Create button press
            #Get text fields
            course_code = form.module_code.data
            course_name = form.module_name.data
            course_desc = form.module_desc.data
            database.create_module_given_head_professor(session['professorid'], course_name, course_desc, course_code)
            return redirect(url_for('modules')) #redirect to modules
        return render_template("professor/professor-create-module.html", form=form) #load create module page
    else:
        return redirect(url_for('home')) #return to home



#Student Exams
@application.route("/exams/", methods=['GET', 'POST'])
@login_required
def exams():
    conn, trans = connect()
    if(session['usertype'] == "professor"): #Professor Exams
        professor_modules = database.get_modules_list_given_professor_id(session['professorid'])
        course_code = "NULL"
        exam_choice = "NULL"
        if request.method == "POST":
            if 'module_buttons' in request.form:
                course_code = request.form.get("module_buttons")
            if 'exam_buttons' in request.form:
                exam_choice = request.form.get("exam_buttons")
        if course_code == "NULL":
            if professor_modules != []:
                course_code = professor_modules[0].ModuleCode
        exams = database.get_exam_as_list(course_code)
        index_exam = ""
        if exams != []:
            index_exam = exams[0]
        if exam_choice != "NULL":
            for exam in exams:
                if exam.Title == exam_choice:
                    index_exam = exam
        session['exam_course_code'] = course_code
        return render_template("professor/professor-exams.html", modules=professor_modules, course_code=course_code, exams=exams, index_exam=index_exam)
    else: #Student Exams
        module_list = database.get_modules_list_given_student_id(session['studentid'])
        course_code = "NULL" #temp code
        empty = False
        if request.method == "POST": #on post
            if 'module_buttons' in request.form: #check if button was pressed
                course_code = request.form.get("module_buttons") #get module_code from button
                module_details_id = database.get_module_id_given_module_code(course_code)
                module_details = database.get_module_given_module_id(module_details_id)
                exams = database.get_exam_list_given_module_id(module_details_id)
                if exams == []:
                    empty = True
        if(course_code == "NULL"): #if button wasn't pressed, set course_code to first registered module
            try: 
                first_module = conn.execute("SELECT * FROM StudentModule WHERE StudentID=%s LIMIT 1", (session['studentid'])) #get first registered module
                for row in first_module:
                    first_moduleid = row[2] #get module id
                module = conn.execute("SELECT ModuleCode FROM CourseModule WHERE ModuleID=%s", (first_moduleid)) #get module information
                for row in module:
                    course_code = row[0] #get module code i.e. COMP202
                module_details_id = database.get_module_id_given_module_code(course_code)
                module_details = database.get_module_given_module_id(module_details_id)
                exams = database.get_exam_list_given_module_id(module_details_id)
                if exams == []:
                    empty = True
            except:
                module_details = None
                exams = None
                empty = True
         
        if(session['usertype'] == "student"):
            return render_template("student/student-exams.html", modules=module_list, course_code=course_code, module_details=module_details, exams=exams, empty=empty)
        elif(session['usertype'] == "courserep"):
            return render_template("courserep/courserep-exams.html", modules=module_list, course_code=course_code, module_details=module_details, exams=exams, empty=empty)



class NewExam(Form):
    #variable names used in html
    exam_name = TextField("")
    exam_desc = TextField("")
    exam_amount = IntegerField("")
class NewQuestion(Form):
    #variable names used in html
    exam_latex = TextField("")
    exam_solution = TextField("")
@application.route("/create-exam/", methods=['GET', 'POST'])
@login_required
def create_exam():
    if(session['usertype'] == "professor"):
        if session.get('created_exam') != True:
            module_id = database.get_module_id_given_module_code(session['exam_course_code'])
            if session.get('create_exam_status') != True:
                form = NewExam(request.form)
                exam_name = ""
                exam_desc = ""
                exam_amount = 0
                if request.method == "POST" and form.validate():
                    exam_name = form.exam_name.data
                    exam_desc = form.exam_desc.data
                    exam_amount = form.exam_amount.data
                    session['create_exam_status'] = True
                    session['exam_name'] = exam_name
                    session['exam_desc'] = exam_desc
                    session['exam_amount'] = exam_amount
                    database.create_exam(module_id, exam_name, exam_desc, 1)
                    return redirect(url_for('create_exam'))
                return render_template("professor/professor-create-exam.html", form=form, created=False)
            else:
                form = NewQuestion(request.form)
                if request.method == "POST" and form.validate():
                    exam_id = database.get_exam_id_given_module_id_title(module_id, session['exam_name'])
                    latex_code = form.exam_latex.data
                    solution_code = form.exam_solution.data
                    database.create_question_template(latex_code, solution_code, 1, exam_id)
                    session['created_exam'] = True
                    return redirect(url_for('create_exam'))
                return render_template("professor/professor-create-exam.html", form=form, created=True)
        else:
            session['create_exam_status'] = None
            session['exam_name'] = None
            session['exam_desc'] = None
            session['exam_amount'] = None
            return redirect(url_for('exams'))
    else:
        return redirect(url_for('home'))


#Student Results
@application.route("/results/", methods=['GET', 'POST'])
@login_required
def results():
    if(session['usertype'] == "student"): #student results
        exams_all = database.get_all_exams_given_student_id(session['studentid'])
        return render_template("student/student-results.html", exams_all=exams_all)
    elif(session['usertype'] == "courserep"): #Course Rep results
        return render_template("courserep/courserep-results.html")
    elif(session['usertype'] == "admin"): #Admin results
        return render_template("admin/admin-results.html")
    else:
        return redirect(url_for('home'))


#Student Settings
#I cant figure out a better way of getting which button was pressed, please help
class SettingsForm(Form):
    btn_reset = TextField("")
    btn_delete = TextField("")
    btn_verification = TextField("")

@application.route("/settings/", methods=['GET', 'POST'])
@login_required
def settings():
    conn, trans = connect()
    form = SettingsForm(request.form)
    if request.method == "POST" and form.validate():
        if 'btn_reset' in request.form:
            #This is where the code for the email sending for resetting a password would go
            return redirect(url_for("settings"))
        elif 'btn_delete' in request.form:
            #Delete account
            try:
                if(session['usertype'] == "professor"): #Professor
                    conn.execute("DELETE FROM Professor WHERE UserID=%s", (session['userid']))
                    conn.execute("DELETE FROM User WHERE UserID=%s", (session['userid']))
                    trans.commit()
                    return redirect(url_for('logout'))
                else: #Every other user
                    conn.execute("DELETE FROM Answered WHERE UserID=%s", (session['userid']))
                    conn.execute("DELETE FROM Cookies WHERE UserID=%s", (session['userid']))
                    conn.execute("DELETE FROM Student WHERE UserID=%s", (session['userid']))
                    conn.execute("DELETE FROM StudentModule WHERE StudentID=%s", (session['studentid']))
                    conn.execute("DELETE FROM User WHERE UserID=%s", (session['userid']))
                    trans.commit()
                    return redirect(url_for('logout'))
            except:
                flash("Oops, something went wrong")
                return redirect(url_for("settings"))
        elif 'btn_verification' in request.form:
            #Request verification
            return redirect(url_for("settings"))
    if(session['usertype'] == "student"):
        return render_template("student/student-settings.html")
    elif(session['usertype'] == "courserep"): #Course Rep settings
        return render_template("courserep/courserep-settings.html")
    elif(session['usertype'] == "professor"): #Professor settings
        return render_template("professor/professor-settings.html")
    elif(session['usertype'] == "admin"): #Admin settings
        return render_template("admin/admin-settings.html")
    else:
        return redirect(url_for('home'))
#Course results
@application.route("/course-results/", methods=['GET', 'POST'])
@login_required
def course_results():
    if(session['usertype'] == "courserep"): #Course rep course-results
        return render_template("courserep/courserep-course.html")
    elif(session['usertype'] == "professor"): #Professor course-results
        return render_template("professor/professor-course.html")
    elif(session['usertype'] == "admin"): #Admin course-results
        return render_template("admin/admin-course.html")

@application.route("/admin/", methods=['GET', 'POST'])
@login_required
def admin():
    if(session['usertype'] == "admin"): #Only admins should have access to this
        return render_template("admin/admin-admin.html")
    else:
        return redirect(url_for('home'))
