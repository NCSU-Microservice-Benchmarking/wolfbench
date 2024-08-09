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

@app.route('/traceless_detections', methods=['POST'])
def traceless_detect():
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
    image = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image.astype(np.float32)
    print("Original image shape:", image.shape)

    # image = np.expand_dims(image, axis=0)

    input_blob = cv2.dnn.blobFromImage(image, scalefactor=1 / 255.0, size=(640, 640), mean=(0, 0, 0),
                                       swapRB=True, crop=False)

    print(f"Input blob shape: {input_blob.shape}")
    ort_inputs = {ort_session.get_inputs()[0].name: input_blob}
    print(f"Model input names: {ort_session.get_inputs()[0].name}")

    try:
        ort_outs = ort_session.run(None, ort_inputs)
        print("ONNX model inference completed successfully.")
    except Exception as e:
        print(f"ONNX model inference failed: {e}")
        return Response(f"ONNX model inference failed: {e}", status=500)

    outputs = ort_outs[0]  # 获取 ONNX 模型的输出
    print(f"Model output shape: {outputs.shape}")
    print(f"Model output sample (first detection): {outputs[0]}")

    results = []

    confidence_threshold = 0.5

    confidence_threshold = 0.5
    for detection in outputs[0]:  # 遍历每个检测框
        x, y, w, h = detection[0:4]
        confidence = detection[4]
        if confidence > confidence_threshold:
            class_probs = detection[5:]
            class_id = np.argmax(class_probs)
            results.append((x, y, w, h, confidence, class_id))

    # Note: Modify as per your actual plotting logic
    for result in results:
        x, y, w, h, confidence, class_id = result
        image = cv2.rectangle(image, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 0), 2)
        image = cv2.putText(image, f'Class: {class_id}, Conf: {confidence:.2f}', (int(x), int(y) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
