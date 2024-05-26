from datetime import datetime
import cv2
import face_recognition
import numpy as np
import pickle
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

ref = db.reference(f'Students/{id}')
bucket = storage.bucket()


################## Defining used parameters
font = cv2.FONT_HERSHEY_TRIPLEX
frameWidth, frameHeight = 640, 480
counter = 0
id = -1
imgStd = []

################## Setting up the webcam
cap = cv2.VideoCapture(0)
cap.set(3, frameWidth)
cap.set(4, frameHeight)


############# Defining modes
modes = ["Active", "Attendance Marked", "Already Marked", "Not Found"]
colorForModes = [(0, 255, 255), (0, 255, 0), (255, 0, 255), (0, 0, 255)]
modeIndex = -1
############# creating background to show result

imgStatus = np.ones((frameHeight, 400, 3), dtype=np.uint8) * 255 ## *255 to have (255,255,255) image

############# Loading the encoding file
file = open("EncodeFile.p", "rb")
encodeListKnownWithIds = pickle.load(file)
encodeListKnown, studentIds = encodeListKnownWithIds
file.close()
print("Encoding file Loaded")


while True:
    _, img = cap.read()
    imgFR = cv2.resize(img, (0,0 ), None, 0.50, 0.50) ## scaling down image to reduce computations
    imgFR = cv2.cvtColor(imgFR, cv2.COLOR_BGR2RGB)

    faceInCurrentFrame = face_recognition.face_locations(imgFR) # locating face in frames
    encodeCurrentFrame = face_recognition.face_encodings(imgFR, faceInCurrentFrame) ##finding encoding of face in frame

    for encodeFace, faceLocation in zip(encodeCurrentFrame, faceInCurrentFrame):
        match = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDistance = face_recognition.face_distance(encodeListKnown, encodeFace)

        matchedIndex = np.argmin(faceDistance)

        if match[matchedIndex]:
            y1, x2, y2, x1 = faceLocation
            y1, x2, y2, x1 = y1*2, x2*2, y2*2, x1*2
            cv2.rectangle(img, (x1, y1), (x2, y2), thickness=2 ,color=(0, 255, 0))
            id = studentIds[matchedIndex]

            if counter == 0 :
                counter = 1
                modeIndex = 1

    if counter != 0:
        # stdInformation = {'department': 'CSE', 'last_attendance_recorded_at': '2024-5-24 00:54:34', 'name': 'Krish Agarwal', 'roll_no': '22ucs108', 'total_attedance': 18}
        if counter == 1:
            stdInformation = db.reference(f'Students/{id}').get()  # Retrieve data

            imgStatus[:] = (255, 255, 255)
            # Get the Image from the storage
            blob = bucket.get_blob(f'Images//{id}.jpg')
            if blob:
                buffer = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStd = cv2.imdecode(buffer, cv2.COLOR_BGRA2BGR)
                imgStd = cv2.resize(imgStd, (216, 216))
                imgStatus[5:221, 90:306] = imgStd
            else:
                print(f"Image not found for student ID: {id}")

            # update date of attendance
            dateTimeInfo = datetime.strptime(stdInformation['last_attendance_recorded_at'], "%Y-%m-%d %H:%M:%S")
            secondsElapsed = (datetime.now() - dateTimeInfo).total_seconds()
            if secondsElapsed > 60*60:
                stdInformation['total_attedance'] += 1  # Increment attendance
                stdInformation['last_attendance_recorded_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                db.reference(f'Students/{int(id)}').set(stdInformation)  # Update document
            else:
                modeIndex = 2
                counter = 10
        if modeIndex != 3:
            if 10 <= counter < 20:

                modeIndex = 2
                cv2.putText(imgStatus, modes[modeIndex], (40, 470), font, 1, colorForModes[modeIndex], 2)
            # imgStatus[80:296, 20:236] = imgStd
            if counter <10:

                cv2.putText(imgStatus, 'Name:', (10, 250), font, 0.8, (0, 0, 0), 2)
                cv2.putText(imgStatus, 'Roll No:', (10, 320), font, 0.8, (0, 0, 0), 2)
                cv2.putText(imgStatus, 'department:', (10, 380), font, 0.8, (0, 0, 0), 2)
                cv2.putText(imgStatus, 'Total Attendance:', (10, 420), font, 0.8, (0, 0, 0), 2)
                cv2.putText(imgStatus, str(stdInformation["name"]), (100, 250), font, 0.8, (0, 0, 255), 2)
                cv2.putText(imgStatus, str(stdInformation["roll_no"]), (130, 320), font, 0.8, (0, 0, 255), 2)
                cv2.putText(imgStatus, str(stdInformation['department']), (200, 380), font, 0.8, (0, 0, 255), 2)
                cv2.putText(imgStatus, str(stdInformation['total_attedance']) , (280, 420), font, 0.8, (0, 0, 255), 2)
                cv2.putText(imgStatus, modes[modeIndex], (40, 470), font, 1, colorForModes[modeIndex], 2)
            counter += 1

            if counter >= 20:
                counter = 0
                modeIndex = 0
                stdInformation = []
                imgStatus[:] = (255, 255, 255)
                cv2.putText(imgStatus, modes[modeIndex], (40, 470), font, 1, colorForModes[modeIndex], 2)
    else:
        modeIndex = 0
        counter = 0
    hStack = np.hstack([img, imgStatus])
    cv2.imshow("Face Attendance", hStack)

    cv2.waitKey(1)
