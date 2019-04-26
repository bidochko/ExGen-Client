from flask import Flask, render_template, redirect, request, send_from_directory, url_for
application = Flask(__name__, static_url_path="")
#, static_url_path="/var/www/ExGenApp/ExGenApp/static"

#from app import routes
import database
#from flask_sqlalchemy import SQLAlchemy

#database.create_student("test", "asddf", "salt")
#database.create_student('user', 'pass', 'salt')
#database.create_professor('profUser', 'pass', 'salt', 'sir', 'prof')
#database.create_module_given_head_professor(1, 'comp', 'comp', 'COMP123')
#database.add_student_to_module(1, 1, False)
#database.delete_one_student_from_module(1, 1)
#database.create_exam(1, 'exam', 'exam', True)
#database.create_question('abc', 'def', True, 1)