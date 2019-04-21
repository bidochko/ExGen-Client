from models import *

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
# Creation functions


def _create_user(username, pw_hash, pw_salt):
    user = User()
    user.UserName = username
    user.Hash = pw_hash
    user.Salt = pw_salt
    db_session.add(user)
    db_session.commit()
    return user

    # private method


def create_student(username, pw_hash, pw_salt):
    user = _create_user(username, pw_hash, pw_salt)
    student = Student()
    student.UserID = user.UserID
    student.isCourseRep = False
    db_session.add(student)
    db_session.commit()


def create_professor(username, pw_hash, pw_salt, professor_name, professor_info):
    user = _create_user(username, pw_hash, pw_salt)
    professor = Professor()
    professor.UserID = user.UserID
    professor.ProfessorName = professor_name
    professor.ProfessorInfo = professor_info
    db_session.add(professor)
    db_session.commit()


def add_student_to_module(student_id, module_id, course_representative):
    student_module = StudentModule()
    student_module.StudentID = student_id
    student_module.ModuleID = module_id
    student_module.CourseRep = course_representative

    db_session.add(student_module)
    db_session.commit()


def add_professor_to_module(professor_id, module_id, head_professor):
    professor_module = ProfessorModule()
    professor_module.ProfessorID = professor_id
    professor_module.ModuleID = module_id
    professor_module.HeadProfessor = head_professor

    db_session.add(professor_module)
    db_session.commit()


def create_module_given_head_professor(professor_id, module_name, module_description, module_code):
    module = CourseModule()
    module.ModuleName = module_name
    module.ModuleDescription = module_description
    module.ModuleCode = module_code

    db_session.add(module)
    db_session.commit()

    module_id = get_module_id_from_module_code(module_code)
    add_professor_to_module(professor_id, module_id, True)


def create_exam(module_id, title, description, enabled):
    exam = Exam()
    exam.ModuleID = module_id
    exam.Title = title
    exam.Description = description
    exam.Enabled = enabled

    db_session.add(exam)
    db_session.commit()


# Get Functions


def get_user_from_user_id(user_id):
    user = db_session.query(User).filter(User.UserID == user_id).first()
    return user


def get_user_from_user_name(user_name):
    user = db_session.query(User).filter(User.UserName == user_name).first()
    return user


def get_student_from_user_id(user_id):
    student = db_session.query(Student).filter(Student.UserID == user_id).first()
    return student


def get_professor_from_user_id(user_id):
    professor = db_session.query(Professor).filter(Professor.UserID == user_id).first()
    return professor


def get_module_id_from_module_code(module_code):
    module = db_session.query(CourseModule).filter(CourseModule.ModuleCode == module_code).first()
    return module.ModuleID


def get_module_id_from_student_id(student_id):
    module = db_session.query(StudentModule).filter(StudentModule.StudentID == student_id)
    return module

    # Returns a list of ModuleIDs


def get_module_id_from_professor_id(professor_id):
    module = db_session.query(ProfessorModule).filter(ProfessorModule.ProfessorID == professor_id)
    return module

    # Returns a list of ModuleIDs


def get_module_from_module_id(module_id):
    module = db_session.query(CourseModule).filter(CourseModule.ModuleID == module_id)
    return module

    # Returns list containing all parts of the module


def get_all_available_modules():
    module = db_session.query(CourseModule)
    return module


def get_full_module_list_from_student_id(student_id):
    module_id_list = get_module_id_from_student_id(student_id)
    module_list = []
    for module_id in module_id_list:
        module = db_session.query(CourseModule).filter(CourseModule.ModuleID == module_id).first()
        module_list.extend(module)
    return module_list

# Delete Functions


def delete_one_student_from_module(student_id, module_id):
    db_session.query(StudentModule).filter(StudentModule.StudentID == student_id, StudentModule.ModuleID == module_id).delete()
    db_session.commit


def delete_one_professor_from_module(professor_id, module_id):
    db_session.query(ProfessorModule).filter(ProfessorModule.ProfessorID == professor_id, ProfessorModule.ModuleID == module_id).delete()
    db_session.commit

    # Think about any difference for head professors


def delete_all_students_from_module(module_id):
    db_session.query(StudentModule).filter(StudentModule.ModuleID == module_id).delete()
    db_session.commit


def delete_all_professors_from_module(module_id):
    db_session.query(ProfessorModule).filter(ProfessorModule.ModuleID == module_id).delete()
    db_session.commit


def delete_module(module_id):
    delete_all_students_from_module(module_id)
    delete_all_professors_from_module(module_id)
    db_session.query(CourseModule).filter(CourseModule.ModuleID == module_id).delete()
    db_session.commit


def delete_exam(exam_id):
    db_session.query(Exam).filter(Exam.ExamID == exam_id).delete()
    db_session.commit


def toggle_exam(exam_id, enabled):
    exam = db_session.query(Exam).filter(Exam.ExamID == exam_id).first()
    if enabled == True and exam.Enabled == False:
        exam.Enabled = True
    elif enabled == False and exam.Enabled == True:
        exam.Enabled = False


def toggle_question(question_template_id, enabled):
    question = db_session.query(Question).filter(Question.QuestionTemplateID == question_template_id).first()
    if enabled == True and question.Enabled == False:
        question.Enabled = True
    elif enabled == False and question.Enabled == True:
        question.Enabled = False






