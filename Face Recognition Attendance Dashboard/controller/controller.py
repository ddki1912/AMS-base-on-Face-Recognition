from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    Response,
    send_file,
    jsonify,
)

import cv2
import pickle
import pandas as pd
import os
import face_recognition
import numpy as np
import urllib
from repository.repository import *
import base64
from controller.esp32 import *
from io import BytesIO
from datetime import datetime

Ctr = Blueprint("controller", __name__)


@Ctr.route("/")
def index():
    return render_template("login.html")


@Ctr.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        id = check_login(username=username, password=password)
        if not (id is None):
            teacher, teacher_img_bytes = get_teacher(id)
            session["teacher"] = teacher
            return redirect("/home")
        else:
            error = "Incorrect username or password!"
            return render_template("login.html", username=username, error=error)


@Ctr.route("/profile")
def profile():
    if not session.get("teacher"):
        return render_template("login.html")

    return render_template(
        "profile.html",
    )


@Ctr.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@Ctr.route("/home")
def home():
    if not session.get("teacher"):
        return render_template("login.html")
    
    students, student_attendance = get_report()
    number_of_students = len(students)
    number_of_attendance = len(student_attendance)

    return render_template("index.html", number_of_students = number_of_students, number_of_attendance=number_of_attendance)


# 192.168.208.251
url_low = "http://192.168.1.24/cam-lo.jpg"
url_mid = "http://192.168.1.24/cam-mid.jpg"
url_high = "http://192.168.1.24/cam-hi.jpg"

known_face_encodings = []
known_face_names = []

print("Loading encoded file ...")
file = open("D:\GitHub\IOT\Face Recognition Attendance Dashboard\EncodeFile.p", "rb")
encoded_known_list_with_ids = pickle.load(file)
file.close()

encoded_known_list, student_id_list = encoded_known_list_with_ids
known_face_encodings = encoded_known_list
known_face_names = student_id_list
print(student_id_list)
print("Encoded file loaded.")

face_locations = []
face_encodings = []
process_frame = True


def get_video_frames(recognition):
    while True:
        # Read camera frame
        img = urllib.request.urlopen(url_high)
        img_np = np.array(bytearray(img.read()), dtype=np.uint8)
        frame = cv2.imdecode(img_np, -1)

        if recognition == 1:
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(
                rgb_small_frame, face_locations
            )
            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(
                    known_face_encodings, face_encoding
                )
                name = "Unknown"

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(
                    known_face_encodings, face_encoding
                )
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    students, student_attendance = get_class_attendance(
                        selected_date=datetime.today().strftime("%Y-%m-%d")
                    )
                    if student_attendance[name] == "":
                        take_student_attendance(
                            name,
                            datetime.today().strftime("%Y-%m-%d"),
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        )

                face_names.append(name)

            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top - 50), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(
                    frame, (left, bottom), (right, bottom + 25), (0, 0, 255), cv2.FILLED
                )
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(
                    frame, name, (left + 6, bottom + 25), font, 1.0, (255, 255, 255), 1
                )

        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@Ctr.route("/video/<int:recognition>")
def get_video(recognition):
    return Response(
        get_video_frames(recognition=recognition),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@Ctr.route("/students")
def manage_students():
    if not session.get("teacher"):
        return render_template("login.html")

    students = get_all_students()
    students_index_list = []
    for key, value in students.items():
        students_index_list.append(value)

    return render_template("manage_student.html", students=students_index_list)


@Ctr.route("/students/<student_id>", methods=["GET", "POST"])
def view_student(student_id):
    if not session.get("teacher"):
        return render_template("login.html")

    error = ""
    student = ""
    student_img = ""
    image_updated = 0

    if request.method == "POST":
        name = request.form.get("name")
        dob = request.form.get("dob")
        tel = request.form.get("tel")
        major = request.form.get("major")
        starting_year = request.form.get("starting_year")
        email = request.form.get("email")
        image_updated = request.form.get("update_student_image")

        if request.form.get("_method") == "POST":
            img = urllib.request.urlopen(url_high)
            img_np = np.array(bytearray(img.read()), dtype=np.uint8)
            frame = cv2.imdecode(img_np, -1)
            frame = cv2.resize(frame, (480, 320))

            file_name = f"imgs/student/{student_id}.jpg"
            cv2.imwrite(filename=file_name, img=frame)

            student = {
                "name": f"{name}",
                "dob": f"{dob}",
                "tel": f"{tel}",
                "student_id": f"{student_id}",
                "major": f"{major}",
                "starting_year": f"{starting_year}",
                "email": f"{email}",
            }

            with open(file_name, "rb") as image:
                student_img = base64.b64encode(image.read()).decode("utf-8")

            return render_template(
                "view_student.html",
                student=student,
                student_img=student_img,
                image_updated=image_updated,
            )

        elif request.form.get("_method") == "PUT":
            img_file_name = f"imgs/student/{student_id}.jpg"
            status = update_student(
                student_id=student_id,
                name=name,
                dob=dob,
                tel=tel,
                major=major,
                starting_year=starting_year,
                email=email,
                img_file_name=img_file_name,
            )
            if status == 1:
                train()
                image_updated = 0
            else:
                error = "Update error!!!"

        elif request.form.get("_method") == "DELETE":
            if delete_student(student_id=student_id) == 1:
                train()
                return redirect("/students")
            else:
                error = "Delete error!!!"

    student, student_img_bytes = get_student(str(student_id))
    student_img = base64.b64encode(student_img_bytes).decode("utf-8")

    return render_template(
        "view_student.html",
        student=student,
        student_img=student_img,
        error=error,
        image_updated=image_updated,
    )


@Ctr.route("/students/add_student", methods=["GET", "POST"])
def add_student():
    if not session.get("teacher"):
        return render_template("login.html")

    message = ""
    error = ""

    if request.method == "POST":
        img = urllib.request.urlopen(url_high)
        img_np = np.array(bytearray(img.read()), dtype=np.uint8)
        frame = cv2.imdecode(img_np, -1)
        frame = cv2.resize(frame, (480, 320))

        name = request.form.get("name")
        dob = request.form.get("dob")
        tel = request.form.get("tel")
        student_id = request.form.get("student_id")
        major = request.form.get("major")
        starting_year = request.form.get("starting_year")
        email = request.form.get("email")

        if not check_existed(student_id=student_id, tel=tel):
            error = "Student existed!!!"
            return render_template(
                "add_student.html",
                name=name,
                dob=dob,
                tel=tel,
                student_id=student_id,
                major=major,
                starting_year=starting_year,
                email=email,
                error=error,
            )

        if (
            add_new_student(
                name=name,
                dob=dob,
                tel=tel,
                student_id=student_id,
                major=major,
                starting_year=starting_year,
                email=email,
                img=frame,
            )
            == 1
        ):
            train()
            message = "Add new face successfully!"
        else:
            error = "Please try again!"

        return render_template("add_student.html", message=message, error=error)

    return render_template("add_student.html")


@Ctr.route("/attendance/take_attendance", methods=["GET"])
def take_attendance():
    if not session.get("teacher"):
        return render_template("login.html")

    today_date = datetime.today().strftime("%Y-%m-%d")
    if check_class_attendance_existed(today_date) == 0:
        add_class_attendance(today_date)

    return render_template("take_attendance.html", today_date=today_date)


@Ctr.route("/load_data")
def count_today_scan():
    if not session.get("teacher"):
        return render_template("login.html")

    students, student_attendance = get_class_attendance(
        selected_date=datetime.today().strftime("%Y-%m-%d")
    )

    students_index_list = []

    for key, value in students.items():
        students_index_list.append(value)

    for key, value in student_attendance.items():
        for i in range(len(students_index_list)):
            if students_index_list[i]["student_id"] == key:
                students_index_list[i]["attendance_time"] = value
                break

    return jsonify(response=students_index_list)


@Ctr.route("/attendance/class_attendance", methods=["POST", "GET"])
def class_attendance():
    if not session.get("teacher"):
        return render_template("login.html")

    if request.method == "POST":
        selected_date = request.form.get("selected_date")

        students, student_attendance = get_class_attendance(selected_date=selected_date)

        students_index_list = []
        if not (students is None) and not (student_attendance is None):
            for key, value in students.items():
                students_index_list.append(value)

            for key, value in student_attendance.items():
                for i in range(len(students_index_list)):
                    if students_index_list[i]["student_id"] == key:
                        students_index_list[i]["attendance_time"] = value
                        break

        return render_template(
            "class_attendance.html",
            selected_date=selected_date,
            students=students_index_list,
        )

    return render_template("class_attendance.html")


@Ctr.route("/attendance/report")
def student_attendance():
    if not session.get("teacher"):
        return render_template("login.html")

    data = {"STT": [], "ID": [], "Name": [], "DOB": [], "Tel": [], "Email": []}
    students_index_list = []

    students, student_attendance = get_report()

    for key, value in students.items():
        students_index_list.append(value)

    for i in range(len(students_index_list)):
        data["STT"].append(i + 1)
        data["ID"].append(students_index_list[i]["student_id"])
        data["Name"].append(students_index_list[i]["name"])
        data["DOB"].append(students_index_list[i]["dob"])
        data["Tel"].append(students_index_list[i]["tel"])
        data["Email"].append(students_index_list[i]["email"])

    for key, value in student_attendance.items():
        data[key] = []
        id_list = []
        time_list = []

        for id, time in value.items():
            id_list.append(id)
            time_list.append(time)

        for id in data["ID"]:
            try:
                index = id_list.index(id)
                if time_list[index] == "":
                    data[key].append("x")
                else:
                    data[key].append("")
            except:
                data[key].append("x")

    df = pd.DataFrame(data)

    attendance_report_file_path = "attendance_report.xlsx"
    class_name = "N10"
    df.to_excel(
        excel_writer=attendance_report_file_path, sheet_name=class_name, index=False
    )

    return send_file(attendance_report_file_path, as_attachment=True)


@Ctr.route("/unlock")
def unlock():
    if not session.get("teacher"):
        return render_template("login.html")

    send_command("open")
    return "Door unlocked!"
