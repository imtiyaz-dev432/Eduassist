import re

def is_valid_email(email):
    pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+$'
    return re.match(pattern,email) is not None

def is_valid_mobile(mobile_no):
     pattern1=r"^[6-9]\d{9}$"
     return re.match(pattern1,mobile_no) is not None

def is_valid_password(password):
    pattern2 = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#_\-]).{8,}$"
    password=password.strip() if password else ""
    return re.match(pattern2,password) is not None 