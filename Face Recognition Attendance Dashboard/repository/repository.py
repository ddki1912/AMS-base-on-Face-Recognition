import firebase_admin
from firebase_admin import db, credentials, storage
import numpy as np
from datetime import datetime
import cv2
import os
import subprocess

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": "https://facerecognitiondatabase-ca552-default-rtdb.asia-southeast1.firebasedatabase.app/",
        "storageBucket": "facerecognitiondatabase-ca552.appspot.com",
    },
)

bucket = storage.bucket()
student_ref = db.reference("student")
teacher_ref = db.reference("teacher")
account_ref = db.reference("account")


def check_login(username=None, password=None):
    try:
        teachers = dict(account_ref.get())

        for key, value in teachers.items():
            if username == value["username"] and password == value["password"]:
                return key

        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_teacher(teacher_id):
    try:
        teacher = dict(teacher_ref.child(f"{teacher_id}").get())
        blob = bucket.get_blob(f"imgs/teacher/{teacher_id}.jpg")
        teacher_img_bytes = blob.download_as_bytes()
        return teacher, teacher_img_bytes
    except Exception as e:
        print(f"Error: {e}")
        return None, None


def get_all_students():
    try:
        students = dict(student_ref.get())
        return students
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_student(student_id):
    try:
        student = dict(student_ref.child(f"{student_id}").get())
        blob = bucket.get_blob(f"imgs/student/{student_id}.jpg")
        student_img_bytes = blob.download_as_bytes()
        return student, student_img_bytes
    except Exception as e:
        print(f"Error: {e}")
        return None, None


def check_existed(student_id, tel):
    students = get_all_students()
    for key, value in students.items():
        if value["tel"] == tel or key == student_id:
            return False

    return True


def add_new_student(name, dob, tel, student_id, major, starting_year, email, img):
    file_name = os.path.join("imgs/student/", str(student_id) + ".jpg")

    data = {
        f"{student_id}": {
            "name": f"{name}",
            "dob": f"{dob}",
            "tel": f"{tel}",
            "student_id": f"{student_id}",
            "major": f"{major}",
            "starting_year": f"{starting_year}",
            "email": f"{email}",
            "total_attendance": 1,
        },
    }

    try:
        cv2.imwrite(filename=file_name, img=img)

        blob = bucket.blob(file_name)
        blob.upload_from_filename(file_name)

        for key, value in data.items():
            student_ref.child(key).set(value)

        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 0


def update_student(
    name,
    dob,
    tel,
    student_id,
    major,
    starting_year,
    email,
    img_file_name,
):
    try:
        student = student_ref.child(f"{student_id}").get()

        student["name"] = name
        student["dob"] = dob
        student["tel"] = tel
        student["major"] = major
        student["starting_year"] = starting_year
        student["email"] = email

        student_ref.child(f"{student_id}").child("name").set(student["name"])
        student_ref.child(f"{student_id}").child("dob").set(student["dob"])
        student_ref.child(f"{student_id}").child("tel").set(student["tel"])
        student_ref.child(f"{student_id}").child("major").set(student["major"])
        student_ref.child(f"{student_id}").child("starting_year").set(
            student["starting_year"]
        )
        student_ref.child(f"{student_id}").child("email").set(student["email"])

        blob = bucket.blob(img_file_name)
        blob.upload_from_filename(img_file_name)

        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 0


def delete_student(student_id):
    try:
        student = db.reference(f"student/{student_id}")
        student.delete()
        file_path = os.path.join("imgs/student/", str(student_id) + ".jpg")
        blob = bucket.blob(file_path)
        blob.delete()
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 0


def train():
    script_path = "D:/B20DCCN352/Year_4/Semester_1/IOT/BTL/EncodeGenerator.py"
    try:
        subprocess.run(["python", script_path], check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error running the script: {e}")
