import datetime
from distutils.log import error, info
from email import message
from sys import modules
from cv2 import CAP_PROP_AUTO_EXPOSURE
from numpy import roll
from website.face_detection import detect_faces, get_face_box
from website.face_recognition import preform_face_recognition
from website.utility_functions import *
from sched import scheduler
from flask import Blueprint, Response, copy_current_request_context, render_template, request, session, url_for, current_app, flash, jsonify, redirect
from flask_login import login_required, current_user
from .models import Student, Attendance, Module
from sqlalchemy import exc
from . import db
import json
from werkzeug.utils import secure_filename
import os
import random
import cv2
import csv
import threading
from flask_apscheduler import APScheduler


# Webcam resolution adjustment
#web_cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
web_cam = cv2.VideoCapture(1)
web_cam.set(cv2.CAP_PROP_FPS, 40.0)
web_cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m', 'j', 'p', 'g'))
web_cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
web_cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
web_cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

views = Blueprint('views', __name__)

scheduler = APScheduler()
scheduler.start()

global start_detection

global capture

capture = 0

image_file_path = ""

global total_detections

total_detections = 0


detection_done = False

start_detection = 0

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def enable_detection():
    global start_detection
    start_detection = 1


def increment_total_detections():
    global total_detections
    total_detections = total_detections + 1

def reset_total_detections():
    global total_detections
    total_detections = 0


def take_snapshot():
    global capture
    capture = 1


my_thread = threading.Thread()


def gen_frames():
    global start_detection
    global capture
    global detection_done
    while True:
        success, frame = web_cam.read()  # read the camera frame
        if not success:
            print("break")
            break
        else:
            if (start_detection):
                start_detection = 0
                file_path = ""
                file_path = os.path.sep.join(
                    ['website/static/session_shots', "shot_{}.jpg".format(str('abc').replace(":", '_'))])
                if (capture):
                    capture = 0
                    file_name = str(random.randint(0, 10)) + '.jpg'
                    print("FILE NAME ", file_name)
                    file_path = os.path.sep.join(
                        ['./website/static/temp/', file_name])
                    print("FILE PATH ", file_path)
                cv2.imwrite(file_path, frame)
                detection_done = detect_faces(file_path)
                print("Detection done")
                print("Picture Taken")
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    data = Attendance.query.all()
    modules_query = Module.query.all()
    session_num = ""

    modules = [(curr.id, curr.module_name) for curr in modules_query]
    module_name = ""

    print("Modules: ", modules)

    if request.method == 'POST':

        if request.form['submit_button'] == 'Detect':

            flash('Detection has been started.', category='info')
            session_num = request.form['session_num']
            module_name = request.form['module_name']

            print("GET: ", session_num)

            print("POST: ", session_num)

            #module_name = db.session.query(Module).filter(Module.id ==selected_module).first()

            # clean_directory(directory='./website/static/query_faces/*')

            # If detection button clicked twice
            if scheduler.get_job('Detection'):
                flash("Detection already started.", category=info)
            else:
                scheduler.remove_all_jobs()

                def clear_query_faces():
                    scheduler.pause_job('clear')
                    clean_directory(directory='./website/static/query_faces/*')
                    scheduler.resume_job('detect')

                @copy_current_request_context
                def start_detection():
                    scheduler.pause_job('detect')
                    print("FACE DETECTION")
                    enable_detection()
                    scheduler.resume_job('rec')

                @copy_current_request_context
                def add_recognised_faces():

                    scheduler.pause_job('rec')

                    query_images = get_images('./website/static/query_faces/')
                    reference_images = get_images('./website/static/upload/')
                    print("PERFORMING FACE RECOGNITION")
                    record_array = preform_face_recognition(
                        query_images=query_images, reference_images=reference_images)
                    

                    if record_array is not None:
                        increment_total_detections()
                        for record in record_array:
                            img_file_path = record[0]
                            student_id = record[1]
                            check_in = record[2]

                            print("TOTAL DETECTIONS: ", total_detections)
                            #percentage = record[3]

                            #new_record = Attendance(img_file_path, student_id, datetime.datetime.now(), check_in, percentage)
                            exists = db.session.query(db.exists().where(
                                Attendance.student_id == student_id)).scalar()

                            try:
                                if not exists:
                                    new_record = Attendance(
                                        img_file_path, student_id, datetime.datetime.now(), 1, total_detections, 100)
                                    db.session.add(new_record)
                                    db.session.commit()
                                    print("Added to database Attendance")
                                    print("HEREE")
                                else:
                                    print("UPDATED DATE")

                                    
                                    student_current = db.session.query(Attendance).filter(
                                        Attendance.student_id == student_id).first()

                                    if check_in == True:
                                        db.session.query(Attendance).filter(Attendance.student_id == student_id).update(
                                            {'present_detections': student_current.present_detections + 1})

                                    db.session.query(Attendance).filter(Attendance.student_id == student_id).update(
                                        {'total_detections': total_detections})


                                    if student_current.present_detections == 0:
                                        percentage_attendance = 0
                                    else:
                                        percentage_attendance = round((student_current.present_detections/total_detections * 100),2)

                                    db.session.query(Attendance).filter(Attendance.student_id == student_id).update(
                                        {'percentage_attendance': percentage_attendance})

                                    db.session.query(Attendance).filter(
                                        Attendance.student_id == student_id).update({'date': datetime.datetime.now()})
                                    db.session.commit()

                            except exc.IntegrityError:
                                db.session.rollback()

                    scheduler.resume_job('clear')

                if scheduler.get_job('rec'):
                    print("sgsgsdgsdgsdgsd")
                else:
                    print("SCHEDULER STARTED")
                    scheduler.add_job(
                        id='rec', func=add_recognised_faces, trigger='interval', seconds=11)
                    scheduler.add_job(
                        id='clear', func=clear_query_faces, trigger='interval', seconds=5)
                    scheduler.add_job(
                        id='detect', func=start_detection, trigger='interval', seconds=10)
                    try:
                        db.session.query(Attendance).delete()
                        db.session.commit()
                        print("Attendance table cleared")
                        # return redirect('/')
                    except:
                        db.session.rollback()
        elif request.form['submit_button'] == 'Cancel':
            flash('Detection has been cancelled.', 'error')
            reset_total_detections()
            scheduler.remove_all_jobs()
            session_num = request.form['session_num']
            data = Attendance.query.all()
            module_name = request.form['module_name']
        elif request.form['submit_button'] == 'Refresh':
            session_num = request.form['session_num']
            module_name = request.form['module_name']
            data = db.session.query(Attendance).all()
            return render_template("home.html", user=current_user, data=data, modules=modules, session_num=session_num, module_name=module_name)
        elif request.form['submit_button'] == 'Export':
            flash("Exported to CSV File", category=info)
            session_num = request.form['session_num']
            module_name = request.form['module_name']
            data = db.session.query(Attendance).all()
            now = datetime.datetime.now()
            str_time_of_save = now.strftime("%d_%m_%Y")
            outfile = open('Attendance_Records/' + str_time_of_save + "_" +
                           str(session_num) + "_" + str(module_name) + ".csv", 'w', newline='')
            outcsv = csv.writer(outfile)
            outcsv.writerow(['Attendance ID', 'Student ID', 'Date',
                            'Present Detections', 'Total Detection', 'Session_Attendance'])

            for curr in data:
                outcsv.writerow([curr.id, curr.student_id, curr.date, curr.present_detections,
                                curr.total_detections, curr.percentage_attendance])
            outfile.close()

    elif request.method == 'GET':

        return render_template("home.html", user=current_user, data=data, modules=modules, session_num=session_num, module_name=module_name)

    session_num = request.form['session_num']
    return render_template("home.html", user=current_user, data=data, modules=modules, session_num=session_num, module_name=module_name)


@views.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    headings = ("Edit", "First Name", "Last Name", "Email", "Delete")
    data = Student.query.all()
    #clean_directory('./'+ current_app.config['TEMP_FOLDER'] + '/*')
    if request.method == 'POST':
        if request.form['submit_button'] == 'Upload':
            clean_directory('./' + current_app.config['TEMP_FOLDER'] + '/*')
            # Upload Picture
            print("Upload Button Pressed")
            if 'file' not in request.files:
                flash('No file part', 'error')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No image selected for uploading', 'error')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename)
                global image_file_path
                image_file_path = os.path.join(
                    current_app.config['TEMP_FOLDER'], filename)
                print(image_file_path)
                file.save(image_file_path)
                #image_file_path = image_file_path[8:]
                flash('Image successfully uploaded and displayed below')
                return render_template('add_student.html', user=current_user, filename=filename, headings=headings, data=data)
            else:
                flash('Allowed image types are - png, jpg, jpeg, gif', 'error')
                return redirect(request.url)
        elif request.form['submit_button'] == 'Capture':
            clean_directory('./' + current_app.config['TEMP_FOLDER'] + '/*')
            enable_detection()
            take_snapshot()
            while True:
                if (len(get_images('./website/static/temp/')) == 1):
                    file_name = get_images('./website/static/temp/')[0][22:]
                    return render_template('add_student.html', user=current_user, filename=file_name, headings=headings, data=data)

        elif request.form['submit_button'] == 'Add Student':
            # Add Student To Database
            print("Add Student Button Pressed")
            req = request.form
            student_first_name = req.get("first_name")
            student_last_name = req.get("last_name")
            student_email = req.get("email")
            student_roll_no = req.get("student_id_num")

            # Check if student already exists in database - email is unique value

            exists = db.session.query(db.exists().where(
                Student.email == student_email)).scalar()

            if not exists and len(student_roll_no) == 8:
                # Remove Image File path validation
                existing_roll_no = db.session.query(
                    Student.student_roll_no).all()

                roll_no = []
                for id_in_row in existing_roll_no:
                    roll_no.append(id_in_row[0])

                while True:
                    if student_roll_no not in roll_no:
                        break
                    else:
                        print("Same roll no has been detected - Re-generating")
                        student_roll_no = generate_student_ID()

                try:
                    uploaded_photo = get_images('./website/static/temp/')[0]
                    print(uploaded_photo)

                    img = get_face_box(uploaded_photo)

                    if img == "Error":
                        flash("More than one face detected in image. Please try again.", category='error')
                    else:

                        file_path = current_app.config['UPLOAD_FOLDER'] + \
                            '/' + str(student_roll_no) + '.jpg'

                        cv2.imwrite(file_path, img)

                        new_record = Student(
                            student_roll_no, student_first_name, student_last_name, student_email, file_path)

                        try:
                            db.session.add(new_record)
                            db.session.commit()
                            flash("Student Added To Database")
                            data = Student.query.all()
                            return render_template('add_student.html', user=current_user, headings=headings, data=data)
                        except exc.IntegrityError:
                            db.session.rollback()
                            flash("Database Integrity Error", "error")
                except IndexError as e:
                    flash("Student image not detected. Please Try Again.", 'error')

            else:
                flash(
                    "Student Record Error. (Note: Student ID must be 8 characters)", "error")
                return render_template('add_student.html', user=current_user, headings=headings, data=data)
    elif request.method == 'GET':
        return render_template('add_student.html', user=current_user, headings=headings, data=data)

    return render_template('add_student.html', user=current_user, headings=headings, data=data)


@views.route('/add_student/delete/<student_email>', methods=['POST'])
def delete_entry(student_email):
    student_to_be_deleted = db.session.query(Student).filter(
        Student.email == student_email).first()
    db.session.delete(student_to_be_deleted)
    db.session.commit()
    # Delete Student Image
    delete_file_from_directory(student_to_be_deleted.img_file_path)
    flash("Student Has Been Deleted", 'error')
    return redirect('/add_student')


@views.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@views.route('/display/<filename>')
def display_image(filename):
    print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='temp/' + filename), code=301)


@views.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
