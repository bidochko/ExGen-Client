from models import *

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


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

# Create Professor method still needs made


def get_user_from_user_id(user_id):
    user = db_session.query(User).filter(User.UserID == user_id).first()
    return user

