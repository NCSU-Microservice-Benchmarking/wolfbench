from flask import Flask, request, Response
import torch
import cv2
import numpy as np
import requests
from ultralytics import YOLO
from flask_cors import CORS, cross_origin



app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Initialize the YOLOv8 model
model = YOLO('yolov8n.pt')  # For a pre-trained model

@app.route('/greet')
def greet():
    return "Hello"

@app.route('/count_gpu')
def countGPU():
    return str(torch.cuda.device_count())

@app.route('/detections', methods=['POST'])
def detect():
    # Retrieve image from the request
    image_file = request.files.get('image')
    image = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)

    # Process the image through YOLOv8
    results = model(image)[0]
    
    # Draw bounding boxes on the image
    # for result in results:
    #     for box_cls_conf in result.boxes:
    #         boxes = box_cls_conf.xyxy.cpu().numpy()
    #         cls_list = box_cls_conf.cls.cpu().numpy()
    #         conf_list = box_cls_conf.conf.cpu().numpy()
    #         for i in range(len(boxes)):
    #             x1, y1, x2, y2 = map(int, boxes[i][:4])
    #             image = cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    #             image = cv2.putText(image, str(conf_list[i]), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    image = results.plot(boxes=True, labels=True, line_width=3, conf=True, probs=False)  # plot a BGR numpy array of predictions

    # Convert the image to a binary string
    image_data = cv2.imencode('.png', image)[1].tobytes()
    return Response(image_data, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)