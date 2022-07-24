import cv2
from rest_framework.response import Response
from django.shortcuts import render

from flask import Flask

# camera = cv2.VideoCapture(0)


app = Flask(__name__)

@app.route('/video')
def getVideo(request):

    return render(request, 'index.html')


if __name__=="__main__":
    app.run(debug=True)