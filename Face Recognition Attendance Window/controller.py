# from flask import Blueprint, redirect, render_template, request, session, Response
# import cv2
# import os
# import face_recognition
# import numpy as np
# import urllib
# # from repository.repository import *

# Ctr = Blueprint("controller", __name__)

# url = "http://192.168.208.251/cam-mid.jpg"

# known_face_encodings = []
# known_face_names = []

# # for file in os.listdir("imgs"):
# #     face_img = face_recognition.load_image_file(file=("imgs/" + file))
# #     face_encoding = face_recognition.face_encodings(face_image=face_img)[0]
# #     known_face_encodings.append(face_encoding)
# #     known_face_names.append(file.removesuffix(".jpg"))

# face_locations = []
# face_encodings = []
# process_frame = True


# def get_video_frames():
#     while True:
#         # Read camera frame
#         img = urllib.request.urlopen(url)
#         img_np = np.array(bytearray(img.read()), dtype=np.uint8)
#         frame = cv2.imdecode(img_np, -1)

#         # # Resize frame of video to 1/4 size for faster face recognition processing
#         # small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)

#         # # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
#         # rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

#         # # Find all the faces and face encodings in the current frame of video
#         # face_locations = face_recognition.face_locations(rgb_small_frame)
#         # face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
#         # face_names = []
#         # for face_encoding in face_encodings:
#         #     # See if the face is a match for the known face(s)
#         #     matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#         #     name = "Unknown"

#         #     # Or instead, use the known face with the smallest distance to the new face
#         #     face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
#         #     best_match_index = np.argmin(face_distances)
#         #     if matches[best_match_index]:
#         #         name = known_face_names[best_match_index]

#         #     face_names.append(name)

#         # # Display the results
#         # for (top, right, bottom, left), name in zip(face_locations, face_names):
#         #     # Scale back up face locations since the frame we detected in was scaled to 1/4 size
#         #     top *= 4
#         #     right *= 4
#         #     bottom *= 4
#         #     left *= 4

#         #     # Draw a box around the face
#         #     cv2.rectangle(frame, (left, top-50), (right, bottom), (0, 0, 255), 2)

#         #     # Draw a label with a name below the face
#         #     cv2.rectangle(frame, (left, bottom), (right, bottom+25), (0, 0, 255), cv2.FILLED)
#         #     font = cv2.FONT_HERSHEY_DUPLEX
#         #     cv2.putText(frame, name, (left + 6, bottom + 25), font, 1.0, (255, 255, 255), 1)

#         ret, buffer = cv2.imencode(".jpg", frame)
#         frame = buffer.tobytes()
#         yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


# @Ctr.route("/video")
# def get_video():
#     return Response(
#         get_video_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
#     )


# @Ctr.route("/streaming")
# def get_home_page():
#     return render_template("streaming.html")


# @Ctr.route("/manage")
# def manage():
#     # if(not session.get("admin")):
#     #     return render_template("login.html")

#     students = []

#     return render_template("manage_student.html", students=students)


# @Ctr.route("/add_student", methods=["GET", "POST"])
# def add_student():
#     # if(not session.get("admin")):
#     #     return render_template("login.html")

#     if request.method == "POST":
#         img = urllib.request.urlopen(url)
#         img_np = np.array(bytearray(img.read()), dtype=np.uint8)
#         frame = cv2.imdecode(img_np, -1)

#         name = request.form.get("name")
#         dob = request.form.get("dob")
#         student_id = request.form.get("student_id")
#         major = request.form.get("major")
#         starting_year = request.form.get("starting_year")
#         year = request.form.get("year")

#         # if add_new_student(
#         #         name=name,
#         #         dob=dob,
#         #         student_id=student_id,
#         #         major=major,
#         #         starting_year=starting_year,
#         #         year=year,
#         #         img=frame,
#         #     ) == 1:
#         #     message = "Add new face successfully!"
#         # else:
#         #     message = "Please try again!"

#         # return render_template("add_student.html", message=message)

#     return render_template("add_student.html")


# @Ctr.route("/student/<student_id>")
# def get_student(student_id):
#     # if(not session.get("admin")):
#     #     return render_template("login.html")

#     student = get_student(student_id)
#     return render_template("add_student.html", student=student)


# @Ctr.route("/update_student/<student_id>", methods=["PUT"])
# def update_student(student_id):
#     # if(not session.get("admin")):
#     #     return render_template("login.html")

#     if request.method == "PUT":
#         return redirect("/manage")


# @Ctr.route("/delete_student/<student_id>", methods=["DELETE"])
# def delete_student(student_id):
#     # if(not session.get("admin")):
#     #     return render_template("login.html")

#     if request.method == "DELETE":
#         return redirect("/manage")
