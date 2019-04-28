from sqlalchemy import not_

from models import *

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=True,
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


def create_student(username, pw_hash, pw_salt, student_id):
    user = _create_user(username, pw_hash, pw_salt)
    student = Student()
    student.StudentID = student_id
    student.UserID = user.UserID
    student.isCourseRep = False
    db_session.add(student)
    db_session.commit()


def create_professor(username, pw_hash, pw_salt, professor_name, professor_info, professor_id):
    user = _create_user(username, pw_hash, pw_salt)
    professor = Professor()
    professor.ProfessorID = professor_id
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

    module_id = get_module_id_given_module_code(module_code)
    add_professor_to_module(professor_id, module_id, True)


def create_exam(module_id, title, description, enabled):
    exam = Exam()
    exam.ModuleID = module_id
    exam.Title = title
    exam.Description = description
    exam.Enabled = enabled

    db_session.add(exam)
    db_session.commit()


def create_question_template(latex_value, solution_code, enabled, exam_id):
    question = QuestionTemplate()
    question.LaTeX = latex_value
    question.SolutionCode = solution_code
    question.Enabled = enabled
    # db_session.add()

    exam = db_session.query(Exam).filter(Exam.ExamID == exam_id).first()
    exam.Questions.append(question)
    db_session.commit()


def create_variable(variable_name, variable_value, question_id):
    variable = Variable()
    variable.VariableName = variable_name
    variable.VariableValue = variable_value
    variable.QuestionID = question_id
    db_session.add(variable)
    db_session.commit()


def create_question(user_id, question_template_id, correct):
    question = Question()
    question.UserID = user_id
    question.QuestionTemplateID = question_template_id
    question.Correct = correct
    db_session.add(question)
    db_session.commit()


# Thought - could create variable when making question but need to know layout for that
# Eg how many variables or a way to do it easily, will leave separate for now


def create_question_answered(user_id, question_id, correct):
    answered_question = AnsweredQuestion()
    answered_question.UserID = user_id
    answered_question.QuestionID = question_id
    answered_question.Correct = correct
    db_session.add(answered_question)
    db_session.commit()


# Get Functions


def get_user_given_user_id(user_id):
    user = db_session.query(User).filter(User.UserID == user_id).first()
    return user


def get_user_given_user_name(user_name):
    user = db_session.query(User).filter(User.UserName == user_name).first()
    return user


def get_student_given_user_id(user_id):
    student = db_session.query(Student).filter(Student.UserID == user_id).first()
    return student


def get_professor_given_user_id(user_id):
    professor = db_session.query(Professor).filter(Professor.UserID == user_id).first()
    return professor


def get_module_id_given_module_code(module_code):
    module = db_session.query(CourseModule).filter(CourseModule.ModuleCode == module_code).first()
    if module:
        return module.ModuleID
    return None


def get_module_ids_given_student_id(student_id):
    module = db_session.query(StudentModule).filter(StudentModule.StudentID == student_id).all()
    return module

    # Returns a list of ModuleIDs


def get_module_ids_given_professor_id(professor_id):
    module = db_session.query(ProfessorModule).filter(ProfessorModule.ProfessorID == professor_id).all()
    return module

    # Returns a list of ModuleIDs


def get_module_given_module_id(module_id):
    module = db_session.query(CourseModule).filter(CourseModule.ModuleID == module_id).first()
    return module


def get_all_available_modules():
    module = db_session.query(CourseModule).all()
    return module


def get_full_module_list_given_student_id(student_id):
    student = get_student_given_student_id(student_id)
    if student:
        return student.StudentModule_List
    return None


def get_modules_list_given_student_id(student_id):
    module_id_list = get_module_ids_given_student_id(student_id)
    modules_list = get_all_available_modules()
    student_modules_list = []
    for module in modules_list:
        inlist = False
        for student_module in module_id_list:
            if module.ModuleID == student_module.ModuleID:
                inlist = True
        if inlist == True:
            student_modules_list.extend([module])
    return student_modules_list


def get_available_modules_given_student_id(student_id):
    module_id_list = get_module_ids_given_student_id(student_id)
    modules_list = get_all_available_modules()
    available_modules = []
    for module in modules_list:
        inlist = False
        for student_module in module_id_list:
            if module.ModuleID == student_module.ModuleID:
                inlist = True
        if inlist == False:
            available_modules.extend([module])
    return available_modules


def get_questions_given_exam_id(exam_id):
    exam = db_session.query(Exam).filter(Exam.ExamID == exam_id).first()
    if exam:
        return exam.Questions
    return None

    # returns a list


def get_student_given_student_id(student_id):
    student = db_session.query(Student).filter(Student.StudentID == student_id).first()
    return student


def get_exam_list_given_module_id(module_id):
    exams = db_session.query(Exam).filter(Exam.ModuleID == module_id).all()
    return exams


def get_all_exams_given_student_id(student_id):
    exams_all = []
    modules = get_modules_list_given_student_id(student_id)
    for module in modules:
        module_exams = get_exam_list_given_module_id(module.ModuleID)
        if module_exams != []:
            exams_all.extend([module_exams])
    return exams_all


# Delete Functions


def delete_one_student_from_module(student_id, module_id):
    student = db_session.query(StudentModule).filter(StudentModule.StudentID == student_id, StudentModule.ModuleID == module_id).first()
    db_session.delete(student)
    db_session.commit()


def delete_one_professor_from_module(professor_id, module_id):
    db_session.query(ProfessorModule).filter(ProfessorModule.ProfessorID == professor_id, ProfessorModule.ModuleID == module_id).delete()
    db_session.commit()

    # Think about any difference for head professors


def delete_all_students_from_module(module_id):
    db_session.query(StudentModule).filter(StudentModule.ModuleID == module_id).delete()
    db_session.commit()


def delete_all_professors_from_module(module_id):
    db_session.query(ProfessorModule).filter(ProfessorModule.ModuleID == module_id).delete()
    db_session.commit()


def delete_module(module_id):
    delete_all_students_from_module(module_id)
    delete_all_professors_from_module(module_id)
    module = db_session.query(CourseModule).filter(CourseModule.ModuleID == module_id).first()
    db_session.delete(module)
    db_session.commit()


def delete_exam(exam_id):
    exam = db_session.query(Exam).filter(Exam.ExamID == exam_id).first()
    db_session.delete(exam)
    db_session.commit()


def delete_user(user_id):
    user = db_session.query(Exam).filter(Exam.ExamID == user_id).first()
    db_session.delete(user)
    db_session.commit()


def delete_student(student_id):
    student = db_session.query(Student).filter(Student.StudentID == student_id).first()
    db_session.delete(student)
    db_session.commit()


def delete_professor(professor_id):
    professor = db_session.query(Professor).filter(Professor.ProfessorID == professor_id).first()
    db_session.delete(professor)
    db_session.commit()


# Misc


def toggle_exam(exam_id, enabled):
    exam = db_session.query(Exam).filter(Exam.ExamID == exam_id).first()
    if enabled == True and exam.Enabled == False:
        exam.Enabled = True
    elif enabled == False and exam.Enabled == True:
        exam.Enabled = False


def toggle_question(question_template_id, enabled):
    question = db_session.query(QuestionTemplate).filter(QuestionTemplate.QuestionTemplateID == question_template_id).first()
    if enabled == True and question.Enabled == False:
        question.Enabled = True
    elif enabled == False and question.Enabled == True:
        question.Enabled = False


def check_user_completed_question(question_id, student_id):
    question = db_session.query(Question).filter(Question.QuestionID == question_id).first()
    if question.Enabled:
        return True
    else:
        return False


# def upgrade_student_to_professor(student_id, professor_name, professor_info, professor_id):
