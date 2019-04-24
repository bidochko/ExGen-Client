import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, BigInteger, Time, Boolean, text
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from config import db_user, db_password, db_host, db_name, db_port

Base = declarative_base()
metadata = Base.metadata
engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(db_user, db_password, db_host, db_port, db_name))


class User(Base):
    __tablename__ = "User"
    UserID = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    UserName = Column(String(128), nullable=False, unique=True)
    Hash = Column(String(128), nullable=False)
    Salt = Column(String(128), nullable=False)
    Professor = relationship("Professor", uselist=False)
    Student = relationship("Student", uselist=False)
    Question_List = relationship("Question")


class Professor(Base):
    __tablename__ = "Professor"
    ProfessorID = Column(Integer, primary_key=True, unique=True, nullable=False)
    ProfessorName = Column(String(128), nullable=False)
    ProfessorInfo = Column(String(128))

    UserID = Column(ForeignKey('User.UserID'), primary_key=False, nullable=False, index=True)
    User = relationship('User', uselist=False)
    ProfessorModule_List = relationship('ProfessorModule')



class Student(Base):
    __tablename__ = "Student"
    StudentID = Column(Integer, primary_key=True, unique=True, nullable=False)
    isCourseRep = Column(Boolean, nullable=False)

    UserID = Column(ForeignKey('User.UserID'), primary_key=False, nullable=False, index=True)
    User = relationship('User', uselist=False)
    StudentModule_List = relationship('StudentModule')


class CourseModule(Base):
    __tablename__ = "CourseModule"
    ModuleID = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    ModuleName = Column(String(128), nullable=False, unique=True)
    ModuleDescription = Column(String(128))
    ModuleCode = Column(String(10), unique=True, nullable=False)
    Exams = relationship('Exam')
    StudentModule_List = relationship('StudentModule')
    ProfessorModule_List = relationship('ProfessorModule')


class Exam(Base):
    __tablename__ = "Exam"
    ExamID = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    Title = Column(String(32), nullable=False)
    Description = Column(String(128))
    Enabled = Column(Boolean, nullable=False)

    ModuleID = Column(ForeignKey('CourseModule.ModuleID'), primary_key=False, nullable=False, index=True)
    CourseModule = relationship('CourseModule')
    Questions = relationship('QuestionTemplate', secondary='Exam_Question')


class QuestionTemplate(Base):
    __tablename__ = "QuestionTemplate"
    QuestionTemplateID = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    LaTeX = Column(String(128), nullable=False)
    SolutionCode = Column(String(128), nullable=False)
    Enabled = Column(Boolean, nullable=False)

    Exams = relationship('Exam', secondary='Exam_Question')
    Question = relationship("Question")


class Variable(Base):
    __tablename__ = "Variable"
    VariableID = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    VariableName = Column(String(32), nullable=False)
    VariableValue = Column(Integer, nullable=False)

    QuestionID = Column(ForeignKey('Question.QuestionID'), primary_key=False, nullable=False, index=True)
    Question = relationship("Question")



class Question(Base):
    __tablename__ = "Question"
    QuestionID = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)

    QuestionTemplateID = Column(ForeignKey('QuestionTemplate.QuestionTemplateID'), primary_key=False, nullable=False, index=True)
    QuestionTemplate = relationship("QuestionTemplate")
    Variable = relationship("Variable")
    AnsweredQuestion = relationship("AnsweredQuestion")


class AnsweredQuestion(Base):
    __tablename__ = "AnsweredQuestion"
    Correct = Column(Boolean, nullable=False)

    UserID = Column(ForeignKey('User.UserID'), primary_key=True, nullable=False, index=True)
    User = relationship("User")
    QuestionID = Column(ForeignKey('Question.QuestionID'), primary_key=True, nullable=False, index=True)
    Question = relationship("Question")


class StudentModule(Base):
    __tablename__ = "StudentModule"
    StudentID = Column(Integer, primary_key=True,  nullable=False)
    ModuleID = Column(Integer, primary_key=True, nullable=False)
    CourseRep = Column(Boolean, nullable=False)

    StudentID = Column(ForeignKey('Student.StudentID'), primary_key=True, nullable=False, index=True)
    Student = relationship("Student")
    ModuleID = Column(ForeignKey('CourseModule.ModuleID'), primary_key=True, nullable=False, index=True)
    CourseModule = relationship("CourseModule")


class ProfessorModule(Base):
    __tablename__ = "ProfessorModule"
    ProfessorID = Column(Integer, primary_key=True, nullable=False)
    ModuleID = Column(Integer, primary_key=True, nullable=False)
    HeadProfessor = Column(Boolean, nullable=False)

    ProfessorID = Column(ForeignKey('Professor.ProfessorID'), primary_key=True, nullable=False, index=True)
    Professor = relationship("Professor")
    ModuleID = Column(ForeignKey('CourseModule.ModuleID'), primary_key=True, nullable=False, index=True)
    CourseModule = relationship("CourseModule")


t_Exam_Question = Table(
    'Exam_Question', metadata,
    Column('ExamID', ForeignKey('Exam.ExamID'), primary_key=True, nullable=False, index=True),
    Column('QuestionTemplateID', ForeignKey('QuestionTemplate.QuestionTemplateID'), primary_key=True, nullable=False,
           index=True)
)

metadata.create_all(bind=engine)