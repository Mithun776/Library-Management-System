import os
import pickle
import cv2
import face_recognition
import cvzone
import numpy as np
from datetime import datetime
from django.core.management.base import BaseCommand
from cse_dept.models import FaceAttendance, Users, AttendanceHistory
from django.conf import settings

class Command(BaseCommand):
    help = 'Attendance Command'

    def handle(self, *args, **kwargs):
        cap = cv2.VideoCapture(0)
        cap.set(3, 640)
        cap.set(4, 480)
        _dir = settings.BASE_DIR / 'cse_dept'
        imgBackgroundPath = os.path.join(_dir, 'images', 'face_attendance', 'background.png')
        imgBackground = cv2.imread(imgBackgroundPath)
        # Importing the mode images into a list
        folderModePath = os.path.join(_dir, 'images', 'face_attendance', 'modes')
        modePathList = os.listdir(folderModePath)
        imgModeList = []
        for path in modePathList:
            imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
        print(len(imgModeList))

        # Load the encoding file
        print("Loading Encode File ...")
        current_dir = os.path.dirname(os.path.realpath(__file__))
        encode_file_path = os.path.join(current_dir, 'EncodeFile.p')
        file = open(encode_file_path, 'rb')
        encodeListKnownWithIds = pickle.load(file)
        file.close()
        encodeListKnown, studentIds = encodeListKnownWithIds
        # print(studentIds)
        print("Encode File Loaded")

        modeType = 0
        counter = 0
        id = -1
        imgStudent = []

        while True:
            success, img = cap.read()

            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            faceCurFrame = face_recognition.face_locations(imgS)
            encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

            imgBackground[162:162 + 480, 55:55 + 640] = img
            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if faceCurFrame:
                for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                    matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                    faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                    # print("matches", matches)
                    # print("faceDis", faceDis)

                    matchIndex = np.argmin(faceDis)
                    # print("Match Index", matchIndex)

                    if matches[matchIndex]:
                        print("Known Face Detected")
                        print(studentIds[matchIndex])
                        y1, x2, y2, x1 = faceLoc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                        imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                        id = studentIds[matchIndex]



                        if counter == 0:
                            cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                            cv2.imshow("EWIT LIBRARY Face Attendance", imgBackground)
                            cv2.waitKey(1)
                            counter = 1
                            modeType = 1

                if counter != 0:

                    if counter == 1:
                        # Get the Data
                        user = Users.objects.get(id_number=str(id))
                        user_details, created = FaceAttendance.objects.get_or_create(
                                user_info=user,
                                defaults={
                                    'last_attendance': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'status': False,
                                    'total': 0
                                }
                            )
                        if created:
                            print(f"Created new FaceAttendance record for user {id}")


                        # Get the Image from the storage
                    pa_th = os.path.join(_dir, 'images', 'faceImages', f'{id}.png')
                    with open(pa_th, 'rb') as f:
                        file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)

                        # Decode the image from the numpy array
                    imgStudent = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                        # Update data of attendance

                    datetimeObject = datetime.strptime(user_details.last_attendance,
                                                           "%Y-%m-%d %H:%M:%S")
                    secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                    print(secondsElapsed)
                    if secondsElapsed > 20:
                        if user_details.status:
                            user_details.status = False
                            history = AttendanceHistory.objects.create(user=user, status=False)
                        else:
                            user_details.total += 1
                            user_details.status = True
                            history = AttendanceHistory.objects.create(user=user, status=True)
                        user_details.last_attendance = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        user_details.save()
                        history.save()
                    else:
                        modeType = 3
                        counter = 0
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                    if modeType != 3:

                        if 10 < counter < 20:
                            modeType = 2

                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                        if counter <= 10:
                            cv2.putText(imgBackground, str(user_details.total), (861, 125),
                                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                            cv2.putText(imgBackground, str(user_details.user_info.id_number), (1006, 550),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                            cv2.putText(imgBackground, str(id), (1006, 493),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                            cv2.putText(imgBackground, str('1'), (910, 625),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                            cv2.putText(imgBackground, str(2), (1025, 625),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                            cv2.putText(imgBackground, str(3), (1125, 625),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                            (w, h), _ = cv2.getTextSize(user_details.user_info.name, cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                            offset = (414 - w) // 2
                            cv2.putText(imgBackground, str(user_details.user_info.name), (808 + offset, 445),
                                        cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                            imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                        counter += 1

                        if counter >= 20:
                            counter = 0
                            modeType = 0
                            studentInfo = []
                            imgStudent = []
                            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
            else:
                modeType = 0
                counter = 0
            # cv2.imshow("Webcam", img)
            cv2.imshow("EWIT LIBRARY Face Attendance", imgBackground)
            cv2.waitKey(1)



