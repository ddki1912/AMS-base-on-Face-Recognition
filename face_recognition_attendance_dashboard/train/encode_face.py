import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np

cred = credentials.Certificate("D:/GitHub/IOT/face_recognition_attendance_dashboard/serviceAccountKey.json")
firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": "https://facerecognitiondatabase-ca552-default-rtdb.asia-southeast1.firebasedatabase.app/",
        "storageBucket": "facerecognitiondatabase-ca552.appspot.com",
    },
)

bucket = storage.bucket()

# Importing student images
img_list = []
student_id_list = []

students = dict(db.reference("student").get())

for key, value in students.items():
    blob = bucket.get_blob(f"imgs/student/{key}.jpg")
    array = np.frombuffer(blob.download_as_string(), np.uint8)
    student_img = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
    img_list.append(student_img)
    student_id_list.append(key)


def encode_face(image_list):
    encoded_face_list = []
    for img in image_list:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        print(encode)
        encoded_face_list.append(encode)

    return encoded_face_list


print("Encoding started ...")
encoded_known_list = encode_face(img_list)
encoded_known_list_with_ids = [encoded_known_list, student_id_list]
print("Encoding completed.")

file = open("D:/GitHub/IOT/face_recognition_attendance_dashboard/train/encoded_file.p", "wb")
pickle.dump(encoded_known_list_with_ids, file)
file.close()
print("File saved.")