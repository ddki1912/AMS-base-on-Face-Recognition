import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": "https://facerecognitiondatabase-ca552-default-rtdb.asia-southeast1.firebasedatabase.app/"
    },
)

ref = db.reference("account")

data = {
    "GV01":{
        "username": "admin",
        "password": "admin",
    }
}

for key, value in data.items():
    ref.child(key).set(value)
