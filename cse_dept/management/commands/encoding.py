import cv2
import face_recognition
import pickle
import os
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Attendance Command'
    # Importing student images
    def handle(self, *args, **options):
        _dir = settings.BASE_DIR / 'cse_dept'
        folderPath = os.path.join(_dir, 'images', 'faceImages')
        pathList = os.listdir(folderPath)
        print(pathList)
        imgList = []
        studentIds = []

        for path in pathList:
            imgList.append(cv2.imread(os.path.join(folderPath, path)))
            studentIds.append(os.path.splitext(path)[0])

            # fileName = f'{folderPath}/{path}'
            # bucket = storage.bucket()
            # blob = bucket.blob(fileName)
            # blob.upload_from_filename(fileName)


            # print(path)
            # print(os.path.splitext(path)[0])
        print(studentIds)


        def findEncodings(imagesList):
            encodeList = []
            for img in imagesList:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                encode = face_recognition.face_encodings(img)[0]
                encodeList.append(encode)

            return encodeList


        print("Encoding Started ...")
        encodeListKnown = findEncodings(imgList)
        encodeListKnownWithIds = [encodeListKnown, studentIds]
        print("Encoding Complete")
        path_ = os.path.join(_dir, 'management/commands/EncodeFile.p')
        file = open(path_, 'wb')
        pickle.dump(encodeListKnownWithIds, file)
        file.close()
        print("File Saved")