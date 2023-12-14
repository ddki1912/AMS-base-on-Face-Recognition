import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from datetime import datetime
import urllib
from esp32 import *

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://facerecognitiondatabase-ca552-default-rtdb.asia-southeast1.firebasedatabase.app/",
    'storageBucket': "facerecognitiondatabase-ca552.appspot.com"
})

bucket = storage.bucket()

# Load all data
print("Loading data ...")
student_info_list = dict(db.reference("student").get())
student_img_list = {}
for key, value in student_info_list.items():
    blob = bucket.get_blob(f'imgs/{key}.jpg')
    array = np.frombuffer(blob.download_as_string(), np.uint8)
    student_img = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
    student_img = cv2.resize(student_img, (216, 216))

    student_img_list[key] = student_img
print("Data loaded.")

background_img = cv2.imread('resources/background.png')

# Import the mode images into a list
mode_folder_path = 'resources/mode'
mode_path_list = os.listdir(mode_folder_path)
mode_img_list = []
for path in mode_path_list:
    mode_img_list.append(cv2.imread(os.path.join(mode_folder_path, path)))

# Load the encoding file
print("Loading encoded file ...")
file = open('D:/B20DCCN352/Year_4/Semester_1/IOT/BTL/EncodeFile.p', 'rb')
encoded_known_list_with_ids = pickle.load(file)
file.close()

encoded_known_list, student_id_list = encoded_known_list_with_ids
print(student_id_list)
print("Encoded file loaded.")

mode_type = 0
counter = 0
id = -1

# Get camera
# 192.168.1.24 or 192.168.208.251
url_low = "http://192.168.1.24/cam-lo.jpg"
url_mid = "http://192.168.1.24/cam-mid.jpg"
url_high = "http://192.168.1.24/cam-hi.jpg"

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

open = False

while True:
    # frame = urllib.request.urlopen(url_high)
    # img_np = np.array(bytearray(frame.read()), dtype=np.uint8)
    # img = cv2.imdecode(img_np, -1)
    # img = cv2.resize(img, (640, 480))
    success, img = cap.read()

    small_img = cv2.resize(img, (0, 0), None, fx=0.25, fy=0.25)
    small_img = cv2.cvtColor(small_img, cv2.COLOR_BGR2RGB)

    face_loc_cur_frame = face_recognition.face_locations(small_img)
    encoded_face_cur_frame = face_recognition.face_encodings(small_img, face_loc_cur_frame)

    background_img[162:162 + 480, 55:55 + 640] = img
    background_img[44:44 + 633, 808:808 + 414] = mode_img_list[mode_type]

    if face_loc_cur_frame:
        for encoded_face, face_loc in zip(encoded_face_cur_frame, face_loc_cur_frame):
            matches = face_recognition.compare_faces(encoded_known_list, encoded_face)
            face_dist = face_recognition.face_distance(encoded_known_list, encoded_face)
            match_index = np.argmin(face_dist)

            if matches[match_index]:
                y1, x2, y2, x1 = face_loc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                background_img = cvzone.cornerRect(background_img, bbox, rt=0)
                id = student_id_list[match_index]
                if counter == 0:
                    cvzone.putTextRect(background_img, "Loading", (300, 400), 2, 1)
                    cv2.imshow("Face Attendance", background_img)
                    cv2.waitKey(1)
                    counter = 1
                    mode_type = 1

        if counter != 0:

            if counter == 1:
                # Get the student info
                student_info = student_info_list[id]   
                print(student_info)

                # Get the student image
                student_img = student_img_list[id]

                # Update data of attendance
                datetime_object = datetime.strptime(student_info['last_attendance_time'],
                                                "%Y-%m-%d %H:%M:%S")
                elapsed_seconds = (datetime.now() - datetime_object).total_seconds()
                print(elapsed_seconds)

                if elapsed_seconds > 30:
                    student_ref = db.reference(f'student/{id}')

                    student_info['total_attendance'] += 1
                    student_ref.child('total_attendance').set(student_info['total_attendance'])
                    student_ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    mode_type = 3
                    open = True
                    counter = 0
                    background_img[44:44 + 633, 808:808 + 414] = mode_img_list[mode_type]

            if mode_type != 3:

                if 10 < counter < 20:
                    mode_type = 2
                    open = True

                background_img[44:44 + 633, 808:808 + 414] = mode_img_list[mode_type]

                # Render student infomation
                if counter <= 10:
                    cv2.putText(background_img, str(student_info['total_attendance']), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(background_img, str(student_info['major']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(background_img, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(background_img, str(student_info['year']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(background_img, str(student_info['starting_year']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(student_info['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(background_img, str(student_info['name']), (808 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    background_img[175:175 + 216, 909:909 + 216] = student_img

                counter += 1

                if counter >= 20:
                    counter = 0
                    mode_type = 0
                    student_info = []
                    student_img = []
                    background_img[44:44 + 633, 808:808 + 414] = mode_img_list[mode_type]
    else:
        mode_type = 0
        counter = 0

    cv2.imshow("Face Attendance", background_img)

    if open:
        time.sleep(1)
        send_command("open")
        open = False

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()