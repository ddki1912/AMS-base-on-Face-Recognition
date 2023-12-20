import subprocess

script1_path = 'D:/GitHub/IOT/face_recognition_attendance_dashboard/app.py'
script2_path = 'D:/GitHub/IOT/face_recognition_attendance_window/main.py'

# Run the scripts in separate processes
process1 = subprocess.Popen(['python', script1_path])
process2 = subprocess.Popen(['python', script2_path])


