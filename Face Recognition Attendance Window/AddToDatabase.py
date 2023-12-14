import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": "https://facerecognitiondatabase-ca552-default-rtdb.asia-southeast1.firebasedatabase.app/"
    },
)

ref = db.reference("/")

today = datetime.today().strftime("%Y-%m-%d")
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# data = {
#     "class": {
#         "attendance": {
#             f"{today}": {
#                 "B20DCCN352": f"{now}",
#             },
#         },
#     }
# }

# data = {
#     "GV01":{
#         "name": "Do Duy Kien",
#         "dob": "2002-12-19",
#         "tel": "0963448172",
#         "email": "ddki1912@gmail.com",
#         "address": "Ha Noi"
#     }
# }

# data = {
#     "B20DCCN352": {
#         "name": "Do Duy Kien",
#         "dob": "2002-12-19",
#         "tel": "0963448172",
#         "student_id": "B20DCCN352",
#         "major": "IT",
#         "starting_year": 2020,
#         "email": "KienDD.B20CN352@stu.ptit.edu.vn",
#     }
# }

# ref.child("student").update(data)
