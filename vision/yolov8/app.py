from flask import Flask, request, Response
import cv2
import numpy as np
import os
from ultralytics import YOLO
from flask_cors import CORS, cross_origin
import onnxruntime as ort

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
app.config['CORS_HEADERS'] = 'Content-Type, Traceparent, Tracestate, Baggage'

# setup opentelemetry
resource = Resource(
    attributes={
        SERVICE_NAME: "vision-microservice-yolov8"
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

# setup tracer
tracer = trace.get_tracer(__name__)

# Initialize the YOLOv8 model
ort_session = ort.InferenceSession('yolov8n.onnx')

@app.route('/greet')
def greet():
    return "Hello"

@app.route('/count_gpu')
def countGPU():
    return "0"
@app.route('/detections_onnx', methods=['POST'])
def detections_onnx():
    # Retrieve image from the request
    image_file = request.files.get('image')

    if image_file:
        print(f"Received image: {image_file.filename}")
        print(f"Image content type: {image_file.content_type}")
        print(f"Image size: {len(image_file.read())} bytes")
        # Reset the file pointer to the beginning after reading
        image_file.seek(0)
    else:
        print("No image file received.")
        return Response("No image file provided", status=400)

    # Decode the image and convert to float32
    image = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)
    print("Original image shape:", image.shape)

    # Convert the image to the required format
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image.astype(np.float32)

    # Resize the image to the required input size of the model
    model_input_size = (640, 640)  # This should match the input size expected by your ONNX model
    image = cv2.resize(image, model_input_size)

    # Normalize the image
    image = image / 255.0
    image = image.transpose((2, 0, 1))  # Change the shape to (C, H, W)
    image = np.expand_dims(image, axis=0)  # Add batch dimension, making the shape (1, C, H, W)

    # Prepare the input for ONNX model
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

    # Process the output from ONNX model
    output = outputs[0]
    output = np.array(output, copy=True)
    print(f"Model output shape: {output.shape}")
    print(f"Model output sample (first detection): {output[0]}")

    detection_raw_result_list = output.squeeze()
    detection_raw_result_list = np.transpose(detection_raw_result_list, (1, 0))

    # Convert raw result to result list in (class, score, x, y, w, h) format
    detection_result_list, average_raw_entropy = detectionRawListToCSXYWH(detection_raw_result_list,
                                                                          object_detection_confidence_threshold=0.5)

    # Apply NMS to the detection results
    detection_result_list = applyNMSForObjectDetection(detection_result_list, object_detection_confidence_threshold=0.5)

    if image.shape[0] == 1:
        image = np.squeeze(image, axis=0)
    print("Image shape after processing:", image.shape)
    if image.shape == (3, 640, 640):
        image = image.transpose(1, 2, 0)

    if image.dtype != np.uint8:
        image = (image * 255).astype(np.uint8)

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    for result in detection_result_list:
        class_idx, class_score, x, y, w, h = result
        image = cv2.rectangle(image, (int(x-w/2), int(y-h/2)), (int(x + w/2), int(y + h/2)), (0, 255, 0), 2)

        # image = cv2.putText(image, f'Class: {str(class_idx)}, Conf: {class_score:.2f}',
        #                     (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    # Encode the image to PNG
    image_data = cv2.imencode('.png', image)[1].tobytes()
    return Response(image_data, mimetype='image/png')


@app.route('/detections', methods=['POST'])
def detect():
    headers = dict(request.headers)

    # Handle Traceparent header
    traceparent = headers.get('Traceparent')
    if traceparent:
        carrier = {'traceparent': traceparent}
        context = TraceContextTextMapPropagator().extract(carrier=carrier)
    else:
        context = None

    # Handle Baggage header
    baggage_header = headers.get('Baggage')
    if baggage_header:
        baggage_dict = {'baggage': baggage_header}
        baggage_context = W3CBaggagePropagator().extract(baggage_dict, context=context)
    else:
        baggage_context = context

    with tracer.start_as_current_span("vision_yolov8_model_process_request", context=baggage_context) as span:
        process_request_context = baggage.set_baggage("context", "vision_yolov8_model_process_request")

        with tracer.start_span("vision_yolov8_model_pre_processing", context=process_request_context):
            # Retrieve image from the request
            image_file = request.files.get('image')

            image = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)

            input_blob = cv2.dnn.blobFromImage(image, scalefactor=1 / 255.0, size=(640, 640), mean=(0, 0, 0),
                                               swapRB=True, crop=False)
            ort_inputs = {ort_session.get_inputs()[0].name: input_blob}
            ort_outs = ort_session.run(None, ort_inputs)
            outputs = ort_outs[0]  # 获取 ONNX 模型的输出

        with tracer.start_span("vision_yolov8_model_inference", context=process_request_context):
            results = []
            for detection in outputs:  # 遍历每个检测框
                x, y, w, h = detection[0:4]  # 获取框的位置
                confidence = detection[4]  # 获取置信度
                class_probs = detection[5:]  # 获取类别分数
                class_id = np.argmax(class_probs)  # 获取类别 ID
                results.append((x, y, w, h, confidence, class_id))

        with tracer.start_span("vision_yolov8_model_post_processing", context=process_request_context):
            # Note: Modify as per your actual plotting logic
            for result in results:
                x, y, w, h, confidence, class_id = result
                image = cv2.rectangle(image, (int(x), int(y)), (int(x+w), int(y+h)), (0, 255, 0), 2)
                image = cv2.putText(image, f'Class: {class_id}, Conf: {confidence:.2f}', (int(x), int(y) - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            image_data = cv2.imencode('.png', image)[1].tobytes()

        with tracer.start_span("vision_yolov8_model_insert_tracing_header", context=process_request_context) as insert_tracing_header_span:
            response_headers = {}
            context = baggage.set_baggage("context", "vision-microservice-yolov8")
            W3CBaggagePropagator().inject(context, response_headers)
            TraceContextTextMapPropagator().inject(response_headers, context)

        return Response(image_data, mimetype='image/png', headers=response_headers)

def convertOutputClassAndWeights(
    output_class_and_weights: np.ndarray,
    crop_detection_confidence_threshold: float = 0.5,
) -> np.ndarray:
    csxywhmws_list = []
    num_rows, num_cols = output_class_and_weights.shape
    for row in range(num_rows):
        x, y, w, h = output_class_and_weights[row, 0:4]
        class_scores = output_class_and_weights[row, 4:4+20]
        mask_weights = output_class_and_weights[row, 4+20:]
        # get the max score
        max_score = class_scores.max()
        if max_score < crop_detection_confidence_threshold:
            continue
        # get the class index
        class_idx = np.argmax(class_scores)
        csxywhmws_list.append([class_idx, max_score, x, y, w, h] + mask_weights.tolist())
    return np.array(csxywhmws_list)


def detectionRawListToCSXYWH(detection_raw_results: np.ndarray, object_detection_confidence_threshold: float) -> np.ndarray:
    csxywh_list = []
    entropy_list = []
    if detection_raw_results.size == 0:
        return np.array(csxywh_list), -1 # return -1 if no detection results
    num_rows, num_cols = detection_raw_results.shape
    for row in range(num_rows):
        x, y, w, h = detection_raw_results[row, 0:4]
        class_scores = detection_raw_results[row, 4:]
        # compute the entropy of the class scores
        entropy = - np.sum(class_scores * np.log(class_scores + 1e-6)) / len(class_scores)
        entropy_list.append(entropy)
        # get the max score
        max_score = class_scores.max()
        if max_score < object_detection_confidence_threshold:
            continue
        # get the class index
        class_idx = np.argmax(class_scores)
        csxywh_list.append([class_idx, max_score, x, y, w, h])
    average_raw_entropy = np.mean(entropy_list) if len(entropy_list) > 0 else -1
    return np.array(csxywh_list), average_raw_entropy

def applyNMSForObjectDetection(detection_result_list: np.ndarray, object_detection_confidence_threshold: float) -> np.ndarray:
    # group detection results by class
    class_dict = {} # class index -> list of detection results
    for detection_result in detection_result_list:
        class_idx = int(detection_result[0])
        if class_idx not in class_dict:
            class_dict[class_idx] = []
        class_dict[class_idx].append(detection_result)
    # apply NMS to each class
    if len(class_dict) == 0: # no detection results, return empty list
        return []
    for class_idx in class_dict:
        class_detection_result_list = np.array(class_dict[class_idx])
        boxes = class_detection_result_list[:, 2:]
        scores = class_detection_result_list[:, 1]
        class_result_indices = cv2.dnn.NMSBoxes(boxes, scores, object_detection_confidence_threshold, 0.5)
        class_dict[class_idx] = class_detection_result_list[class_result_indices]
    # merge the detection results
    detection_result_list = []
    for class_idx in class_dict:
        detection_result_list.extend(class_dict[class_idx])
    return detection_result_list


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
