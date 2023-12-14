import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": "https://facerecognitiondatabase-ca552-default-rtdb.asia-southeast1.firebasedatabase.app/",
        "storageBucket": "facerecognitiondatabase-ca552.appspot.com",
    },
)

bucket = storage.bucket()

# Importing student images
imgList = []
studentIds = []

students = dict(db.reference(f"student").get())

for key, value in students.items():
    blob = bucket.get_blob(f"imgs/student/{key}.jpg")
    array = np.frombuffer(blob.download_as_string(), np.uint8)
    imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
    imgList.append(imgStudent)
    studentIds.append(key)


def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        print(encode)
        encodeList.append(encode)

    return encodeList


print("Encoding Started ...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print(encodeListKnownWithIds)
print("Encoding Complete")

file = open("EncodeFile.p", "wb")
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")
