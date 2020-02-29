from django.shortcuts import render
from django.http import HttpResponse,StreamingHttpResponse
from django.views.decorators import gzip
from django.views.decorators.clickjacking import xframe_options_exempt
import os
import cv2
import time

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('H', '2', '6', '4'));
        self.cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')
        
    def __del__(self):
        #self.video.release()
        print('A')

    def convert_frame(self ,image):
        gray = cv2.cvtColor(image ,cv2.COLOR_BGR2GRAY)
        facerect = self.cascade.detectMultiScale(
            gray,
            scaleFactor=1.11,
            minNeighbors=3,
            minSize=(30, 30)
        )
        if 0 != len(facerect):
            BORDER_COLOR = (255, 255, 255) # 線色を白に
            for rect in facerect:
                # 顔検出した部分に枠を描画
                cv2.rectangle(
                    image,
                    tuple(rect[0:2]),
                    tuple(rect[0:2] + rect[2:4]),
                    BORDER_COLOR,
                    thickness=2
                )
        return image

    def get_frame(self):
        ret,image = self.video.read()
        image = self.convert_frame(image)
        ret,jpeg = cv2.imencode('.jpg',image)
        return jpeg.tobytes()

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def index(request):
    return render(request ,'index.html')

@ gzip.gzip_page
@ xframe_options_exempt
def capture(request):
    # response = HttpResponse(gen(VideoCamera())
    return StreamingHttpResponse(gen(VideoCamera()),content_type='multipart/x-mixed-replace; boundary=frame')
