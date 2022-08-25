# Facial Expression Recognition & Analyzer and Report
import time

import cv2
import socket
import json
import logging
import threading
from deepface import DeepFace

FORMAT = "%(asctime)-15s %(levelname)s %(process)d %(message)s"
logging.basicConfig(filename="GenesysFERClient.log", level=logging.DEBUG, format=FORMAT)
log = logging.getLogger("GenesysFERClient")
SCons = ""



serverIP = "172.24.132.174"
serverPort = 9090
loop = False


def start_analyzing_mimic():
    emotions = {
        "angry": 0,
        "disgust": 0,
        "fear": 0,
        "happy": 0,
        "sad": 0,
        "surprise": 0,
        "neutral": 0
    }
    while not loop:
        time.sleep(0.1)
        continue

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise IOError("No camera detected")

    while loop:
        ret, frame = cap.read()
        result_analyzer = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        font = cv2.FONT_HERSHEY_PLAIN
        # print('Dominant Facial Expression {0}'.format(result_analyzer['dominant_emotion']))
        analyze_expressions(result_analyzer['emotion'],emotions)
        #result = json.dumps(result_analyzer['emotion'])
        #send_data(result)

        cv2.putText(frame, result_analyzer['dominant_emotion'], (50, 50), font, 3, (0, 0, 255), 2, cv2.LINE_4)
        cv2.imshow('Original video', frame)

        if cv2.waitKey(2) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    send_data(emotions)


def analyze_expressions(emotion, emotions):
    for key in emotion:
        emotions[key] = emotions[key] + emotion[key];


def report_expressions(emotions):
    total = 0;
    data = {}
    for key in emotions:
        total += emotions[key];
    for key in emotions:
        percentage = round(emotions[key] * 100 / total, 2);
        value = percentage
        data[key] = value
    return json.dumps(data)


def send_data(emotions):
    global SCons
    try:
        data = report_expressions(emotions)
        print(data)
        SCons.send(data.encode('utf-8'))
    except:
        log.warning("unable to send data to %s:%d" % (serverIP, serverPort))


def createConnection():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object.
        s.connect((serverIP, serverPort))
    except:
        print("unable to connect to %s:%d" % (serverIP, serverPort))
        return 0
    print("Connected to %s:%d" % (serverIP, serverPort))
    return s


def initClient():
    global SCons, loop
    SCons = createConnection()
    while True:
        if SCons:
            data = SCons.recv(1024)
            if data:
                event = data.decode('utf-8')
                print(event)
                if event == "EventStartVideo":
                    loop = True
                else:
                    loop = False
        else:
            log.warning("connecting to server  %s:%d failed, reconnect happens every 5 sec .." % (serverIP, serverPort))
            time.sleep(5)


def main():
    t1 = threading.Thread(target=initClient)
    #t2 = threading.Thread(target=start_analyzing_mimic)
    t1.start()
    while True:
        start_analyzing_mimic()
    #t2.start()
    #t1.join()
    #t2.join()

if __name__ == '__main__':
    main()
