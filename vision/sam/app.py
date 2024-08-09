from traceback import print_tb

import onnxruntime as ort
from flask import Flask, request, Response
import cv2
import numpy as np
import requests
import os
from flask_cors import CORS, cross_origin

from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from opentelemetry import trace, propagators, baggage
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Setup opentelemetry
resource = Resource(
    attributes={
        SERVICE_NAME: "vision-microservice-sam"
    }
)

jaeger_endpoint = os.getenv("TRACE_COLLECTOR_ENDPOINT", "http://jaeger-with-cassandra-and-kafka-collector.observability.svc.cluster.local:4318")

trace_provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=jaeger_endpoint + "/v1/traces"))
trace_provider.add_span_processor(processor)
trace.set_tracer_provider(trace_provider)

reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=jaeger_endpoint + "/v1/metrics")
)

meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(meter_provider)

# Setup tracer
tracer = trace.get_tracer(__name__)

# Load a model
# model = SAM('sam_b.pt')
# Initialize the YOLOv8 model
ort_session = ort.InferenceSession('yolov8n.onnx')

# Initialize the model
# model = torch.hub.load('yolov5', 'custom', path='yolov5s.pt', source='local')
# model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
# model.eval()

@app.route('/greet')
def greet():
    return("Hello")

import onnxruntime as ort
from flask import Flask, request, Response
import cv2
import numpy as np

app = Flask(__name__)

# Load the YOLOv8 segmentation model
ort_session = ort.InferenceSession('yolov8n-seg.onnx')

@app.route('/segment_onnx', methods=['POST'])
def segment_onnx():
    # Retrieve image from the request
    image_file = request.files.get('image')

    if not image_file:
        print("No image file received.")
        return Response("No image file provided", status=400)

    print(f"Received image: {image_file.filename}")
    print(f"Image content type: {image_file.content_type}")
    image_size = len(image_file.read())
    print(f"Image size: {image_size} bytes")
    image_file.seek(0)  # Reset file pointer after reading

    # Decode the image and convert to float32
    image = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)
    print("Original image shape:", image.shape)

    # Preprocess the image
    image = preprocess_image(image)

    # Prepare input for the ONNX model
    input_name = ort_session.get_inputs()[0].name
    output_name_list = [output.name for output in ort_session.get_outputs()]
    print(f"Input blob shape: {image.shape}")
    print(f"Model input names: {input_name}")

    try:
        # Perform inference
        outputs = ort_session.run(output_name_list, {input_name: image})
        print("ONNX model inference completed successfully.")
    except Exception as e:
        print(f"ONNX model inference failed: {e}")
        return Response(f"ONNX model inference failed: {e}", status=500)

    # Process and post-process the output

    class_mask_dict = postprocess_output(outputs)
    # Apply masks to the original image
    segmented_image = apply_masks_to_image(image, class_mask_dict)
    segmented_image = segmented_image.astype(np.uint8)
    # Encode the image to PNG and return as response
    segmented_image = segmented_image.transpose((2, 0, 1))
    print("segmented image shape:", segmented_image.shape)

    image_data = cv2.imencode('.png', segmented_image)[1].tobytes()
    return Response(image_data, mimetype='image/png')


def preprocess_image(image):
    """Preprocess the input image to the format required by the ONNX model."""
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image.astype(np.float32)
    image = cv2.resize(image, (640, 640))  # Resize to the model's input size
    image = image / 255.0
    image = image.transpose((2, 0, 1))  # Change shape to (C, H, W)
    image = np.expand_dims(image, axis=0)  # Add batch dimension (1, C, H, W)
    return image


def postprocess_output(outputs):
     # do inference
    model_input_size = (640,640)
    # get the output_0 and output_1
    output_0 = outputs[0] # 1 x 56 x 336: 336 predicted masks with (xc, yc, w, h, cls_conf1, cls_conf2, ..., cls_conf20, mask_weight1, mask_weight2, ..., mask_weight32)
    output_1 = outputs[1] # 1 x 32 x 80 x 80: 32 masks in shape (80, 80) # NOTE: this is because YOLOv8 model outputs a 80x80 mask. Need to be configured if the model changes
    output_0 = np.array(output_0, copy=True)
    output_1 = np.array(output_1, copy=True)
    # get the masks and weights by transpose from 1x56x336 to 56x336 and 1x32x32x32 to 32x32x32
    output_class_and_weights = np.transpose(output_0[0], (1, 0))
    output_masks = np.transpose(output_1[0], (1, 2, 0))
    crop_detection_confidence_threshold = 0.5
    # convert output class and weights to class, score, xc, yc, w, h, [mw1, mw2, ..., mw32]
    output_class_and_weights = convertOutputClassAndWeights(output_class_and_weights, crop_detection_confidence_threshold)
    # apply NMS to the output class and weights
    output_class_and_weights = applyNMSForCropMonitoring(output_class_and_weights, crop_detection_confidence_threshold)
    # split the output class and weights by class
    class_mask_dict, image_avg_entropy = combineClassWeightsAndMasks(output_class_and_weights, output_masks, crop_detection_confidence_threshold, model_input_size[0], model_input_size[1])
    print("class_mask_dict", class_mask_dict)
    return  class_mask_dict


def apply_masks_to_image(image, class_mask_dict):
    """Apply the segmentation masks to the original image."""
    image = np.squeeze(image)
    print("Original image shape:", image.shape)

    # 图像的形状应为 (C, H, W)
    image_c, image_h, image_w = image.shape

    for class_id, mask in class_mask_dict.items():
        # Resize mask to match the height and width of the original image
        resized_mask = cv2.resize(mask, (image_w, image_h))
        binary_mask = (resized_mask > 0.5).astype(np.uint8)  # Convert to binary mask
        binary_mask = np.expand_dims(binary_mask, axis=0)  # Add channel dimension, making it (1, H, W)

        print("Image shape:", image.shape)
        print("Mask shape:", binary_mask.shape)

        # Apply the mask to each channel of the image
        for c in range(image_c):
            image[c] = image[c] * binary_mask

    # 如果需要将图像转换回 `HWC` 格式，可以使用 `image = np.transpose(image, (1, 2, 0))`
    return image

@app.route('/',methods=['POST'])
def segment():
    headers = dict(request.headers)
    print(headers)
    carrier = {'traceparent': headers['Traceparent']}
    context = TraceContextTextMapPropagator().extract(carrier=carrier)

    baggage_dict ={'baggage': headers['Baggage']}
    baggage_context = W3CBaggagePropagator().extract(baggage_dict, context=context)

    with tracer.start_as_current_span("vision_sam_model_process_request", context=baggage_context):
        process_request_context = baggage.set_baggage("context", "vision_sam_model_process_request")

        with tracer.start_span("vision_sam_model_pre_processing", context=process_request_context):
            # get image from the request form
            image = request.files.get('image')
            image = image.read()
            # convert image string to a numpy array
            nparr = np.frombuffer(image, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Process the image through sam
        with tracer.start_span("vision_sam_model_inference", context=process_request_context):
            # Run inference
            results = model(image)[0]

        # Post-process the results
        with tracer.start_span("vision_sam_model_post_processing", context=process_request_context):
            image = results.plot(boxes=False, labels=False, probs=False, conf=True)  # plot a BGR numpy array of predictions
            # convert image to a binary string
            image = cv2.imencode('.png', image)[1].tobytes()

        # Add context to the span in response headers
        with tracer.start_span("vision_sam_model_insert_tracing_header", context=process_request_context) as insert_tracing_header_span:
            headers = {}
            context = baggage.set_baggage("context", "vision-microservice-sam")
            W3CBaggagePropagator().inject(context, headers)
            TraceContextTextMapPropagator().inject(headers, context)

        # send the image to the client as an png image encoded as a binary string
        return Response(image, mimetype='image/png', headers=headers)

def convertOutputClassAndWeights(
    output_class_and_weights: np.ndarray,
    crop_detection_confidence_threshold: float = 0.5,
) -> np.ndarray:
    csxywhmws_list = []
    num_rows, num_cols = output_class_and_weights.shape
    for row in range(num_rows):
        x, y, w, h = output_class_and_weights[row, 0:4]
        class_scores = output_class_and_weights[row, 4:4+80]
        mask_weights = output_class_and_weights[row, 4+80:]
        # get the max score
        max_score = class_scores.max()
        if max_score < crop_detection_confidence_threshold:
            continue
        # get the class index
        class_idx = np.argmax(class_scores)
        csxywhmws_list.append([class_idx, max_score, x, y, w, h] + mask_weights.tolist())
    return np.array(csxywhmws_list)

def combineClassWeightsAndMasks(class_and_weights: list, output_masks: np.ndarray, crop_detection_mask_threshold: float = 0.5, image_tile_width: float = 320, image_tile_height: float = 320) -> np.ndarray:
    # transpose output_masks from 80 x 80 x 32 to 32 x 80 x 80
    output_masks = np.transpose(output_masks, (2, 0, 1))
    # sum up all the weights for the same class
    class_mask_weight_dict = {} # class index -> mask weights
    for i in range(len(class_and_weights)):
        class_idx = int(class_and_weights[i][0])
        mask_weight = class_and_weights[i][6:]
        # broad cast the mask weight from N to N x 1 x 1
        mask_weight = mask_weight.reshape(-1, 1, 1)
        if class_idx not in class_mask_weight_dict:
            class_mask_weight_dict[class_idx] = mask_weight
        class_mask_weight_dict[class_idx] += mask_weight
    # check if there exists valid class mask weight dict
    if len(class_mask_weight_dict) == 0:
        return {}, None
    # get the masks for each class
    dict_mask_idx_class_idx = {} # index in the composite mask -> class index
    for mask_idx, class_idx in enumerate(class_mask_weight_dict.keys()):
        dict_mask_idx_class_idx[mask_idx] = class_idx
    masks = []
    for class_idx, mask_weight in class_mask_weight_dict.items():
        # mask_weight's shape is 32
        # output_masks' shape is 32 x 80 x 80
        # class mask is the sum of output_mask[i] * every value in mask_weight[i] for i in range(len(mask_weight))
        class_mask = np.sum(output_masks * mask_weight, axis=0)
        masks.append(class_mask)
    # check if there exists valid masks
    if len(masks) == 0:
        return {}, None
    # stack the masks
    masks = np.stack(masks)
    # apply sigmoid to the masks
    masks = 1 / (1 + np.exp(-masks))
    # from masks calculate the entropy as - masks[i, j, k] * log(masks[i, j, k])
    entropy = -np.sum(masks * np.log(masks + 1e-6)) / masks.size
    # filter out the masks with the mask threshold
    masks = (masks > crop_detection_mask_threshold) * 1.0
    # resize the masks from N x 80 x 80 to N x image_tile_height x image_tile_width
    masks = np.array([cv2.resize(mask, (image_tile_width, image_tile_height)).T for mask in masks])
    # distribute the masks to the class_mask_dict
    class_mask_dict = {} # class index -> mask
    for mask_idx in range(len(masks)):
        class_idx = dict_mask_idx_class_idx[mask_idx]
        class_mask_dict[class_idx] = masks[mask_idx]
        # # # draw the mask
        # cv2.imwrite(f"mask_{class_idx}.png", masks[mask_idx] * 255)
    return class_mask_dict, entropy

def applyNMSForCropMonitoring(
    detection_result_list: np.ndarray,
    crop_detection_confidence_threshold: float = 0.5,
) -> np.ndarray:
    # group detection results by class
    class_dict = {} # class index -> list of detection results
    for detection_result in detection_result_list:
        class_idx = int(detection_result[0])
        if class_idx not in class_dict:
            class_dict[class_idx] = []
        class_dict[class_idx].append(detection_result)
    # apply NMS to each class
    for class_idx in class_dict:
        class_detection_result_list = np.array(class_dict[class_idx])
        boxes = class_detection_result_list[:, 2:6]
        scores = class_detection_result_list[:, 1]
        class_result_indices = cv2.dnn.NMSBoxes(boxes, scores, crop_detection_confidence_threshold, 0.5)
        # filter out the detection results
        class_dict[class_idx] = class_detection_result_list[class_result_indices]
    # merge the detection results
    detection_result_list = []
    for class_idx in class_dict:
        detection_result_list.extend(class_dict[class_idx])
    return detection_result_list

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)