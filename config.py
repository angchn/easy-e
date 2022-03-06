import os

#config database "students.db"
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'correcthorsebatterystaple'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///student.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SQLALCHEMY_ECHO = False