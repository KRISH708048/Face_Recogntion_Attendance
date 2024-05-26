import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import os


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://facerecognitionbasedattendence-default-rtdb.firebaseio.com/",
    'storageBucket' : "facerecognitionbasedattendence.appspot.com"
})

ref = db.reference('Students')

data = {
    '108' : {
        "name" : "Krish Agarwal",
        "department" : "CSE",
        "roll_no" : "22ucs108",
        "total_attedance" : 6,
        "last_attendance_recorded_at" : "2024-5-24 00:54:34"
    },
    '001' : {
        "name" : "Aakash Chauhan",
        "department" : "CSE",
        "roll_no" : "22ucs001",
        "total_attedance" : 6,
        "last_attendance_recorded_at" : "2024-5-24 00:54:34"
    },
    '237' : {
        "name" : "Hitanshu Satpathy",
        "department" : "CSE",
        "roll_no" : "22ucs237",
        "total_attedance" : 6,
        "last_attendance_recorded_at" : "2024-5-24 00:54:34"
    },
    '1000' : {
        "name" : "Kshitij Sharma",
        "department" : "CSE",
        "roll_no" : "1000IITBHU",
        "total_attedance" : 6,
        "last_attendance_recorded_at" : "2024-5-24 00:54:34"
    },
    '1001' : {
        "name" : "Papa",
        "department" : "Father",
        "roll_no" : "1",
        "total_attedance" : 6,
        "last_attendance_recorded_at" : "2024-5-24 23:54:34"
    }
    ,'1002' : {
        "name" : "mumma",
        "department" : "Mother",
        "roll_no" : "1",
        "total_attedance" : 6,
        "last_attendance_recorded_at" : "2024-5-24 23:54:34"
    }
}

for key,value in data.items():
    ref.child(key).set(value)


path = "Images/"
pathList = os.listdir(path)

for img in pathList:
    fileName = f'{path}/{img}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

print("Data Added Successfully")