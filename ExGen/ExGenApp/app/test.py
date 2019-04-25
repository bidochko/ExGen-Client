from db import database

student_id = 201275923
username = "test"
randomSalt = "haha"
password = "killme"

module_list = database.get_modules_list_given_student_id(student_id)
for module in module_list:
    print(module.ModuleName)