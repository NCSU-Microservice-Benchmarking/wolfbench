from ultralytics import SAM
from flask import Flask, request, Response
import torch
import cv2
import numpy as np
import requests
from flask_cors import CORS, cross_origin



app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Load a model
model = SAM('sam_b.pt')

# initial the model
# model = torch.hub.load('yolov5', 'custom', path='yolov5s.pt', source='local')
# model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
# model.eval()

@app.route('/greet')
def greet():
    return("Hello")


@app.route('/count_gpu')
def countGPU():
        return str(torch.cuda.device_count())

@app.route('/',methods=['POST'])
def segment():
    # get image from the request form
    image = request.files.get('image')
    image = image.read()
    # convert image string to a numpy array
    nparr = np.fromstring(image, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR) # cv2.IMREAD_COLOR in OpenCV 3.1
    # Run inference
    results = model(image)
    for r in results:
        image = r.plot()  # plot a BGR numpy array of predictions
    # convert image to a binary string
    image = cv2.imencode('.png', image)[1].tostring()
    # send the image to the client as an png image encoded as a binary string
    return Response(image, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)