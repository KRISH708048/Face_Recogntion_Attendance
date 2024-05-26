import cv2
import os
import face_recognition
import pickle

######## import the images
path = "Images/"
pathList = os.listdir(path)
imageList = []
stdIds = []
for img in pathList:
    imageList.append(cv2.imread(os.path.join(path, img)))
    stdIds.append(img.split('.')[0])

print("Number of Student Enrolled:", len(imageList))


def generate_encoding(imgList):
    encodeList = []
    for img in imgList:
        # converting img from BGR to RGB , face-recognition: default schem RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList


print("encoding started.....")
knownEncodeList = generate_encoding(imageList)
print("encoding of images completed")

# print(knownEncodeList[0])

# storing in file
file = open("EncodeFile.p", "wb")
pickle.dump([knownEncodeList,stdIds], file)
file.close()
print("encodings saved in file")