from email.policy import default
from enum import unique
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    #notes = db.relationship('Note')

class Student(db.Model):
    student_roll_no = db.Column(db.Integer, primary_key=True, nullable=False)
    f_name = db.Column(db.String(50), nullable=False)
    l_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    img_file_path = db.Column(db.String(200), unique=True, nullable=False)

    def __init__(self,student_roll_no, f_name, l_name, email, img_path):
        self.student_roll_no = student_roll_no
        self.f_name = f_name
        self.l_name = l_name
        self.email = email
        self.img_file_path = img_path

class Module(db.Model):
    id = db.Column(db.String(150), unique=True,  primary_key=True) # Module ID
    module_name = db.Column(db.String(150), nullable=False) # Module Name

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img_file_path = db.Column(db.String(200), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_roll_no'))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    present_detections = db.Column(db.Integer, default=0)
    total_detections = db.Column(db.Integer, default=0)
    percentage_attendance = db.Column(db.Float, default=0)

    def __init__(self,img_file_path,student_id,date, present_detections,total_detections, percentage_attendance):
        self.img_file_path = img_file_path
        self.student_id = student_id
        self.date = date
        self.present_detections = present_detections
        self.total_detections = total_detections
        self.percentage_attendance = percentage_attendance