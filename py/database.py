from models import *

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


def create_user(username, pw_hash, pw_salt):
    user = User()
    user.UserName = username
    user.Hash = pw_hash
    user.Salt = pw_salt
    db_session.add(user)
    db_session.commit()
    return user


def create_student(username, pw_hash, pw_salt):
    user = create_user(username, pw_hash, pw_salt)
    student = Student()
    student.UserID = user.UserID
    student.isCourseRep = False
    db_session.add(student)
    db_session.commit()