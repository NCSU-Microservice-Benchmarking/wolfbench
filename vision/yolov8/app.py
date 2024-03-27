from flask import Flask, request, Response
import torch
import cv2
import numpy as np
import requests
import os
from ultralytics import YOLO
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

# setup opentelemetry
resource = Resource(
    attributes={
        SERVICE_NAME: "vision-microservice-yolov8"
    }
)

# jaeger_endpoint = "http://jaeger-with-cassandra-and-kafka-collector.observability.svc.cluster.local:4317"
# jaeger_endpoint = "http://eb2-2259-lin04.csc.ncsu.edu:30318"

jaeger_endpoint = os.getenv("JAEGER_ENDPOINT", "http://localhost:4317")

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
model = YOLO('yolov8n.pt')  # For a pre-trained model

@app.route('/greet')
def greet():
    return "Hello"

@app.route('/count_gpu')
def countGPU():
    return str(torch.cuda.device_count())

@app.route('/detections', methods=['POST'])
def detect():
    headers = dict(request.headers)
    print(headers)
    carrier = {'traceparent': headers['Traceparent']}
    context = TraceContextTextMapPropagator().extract(carrier=carrier)

    baggage_dict ={'baggage': headers['Baggage']}
    baggage_context = W3CBaggagePropagator().extract(baggage_dict, context=context)

    with tracer.start_span("vision_yolov8_model_process_request", context=baggage_context) as span:
        process_request_context = baggage.set_baggage("context", "vision_yolov8_model_process_request")
        # set pre_processing context
        with tracer.start_span("vision_yolov8_model_pre_processing", context=process_request_context) as pre_processing_span:
            # Retrieve image from the request
            image_file = request.files.get('image')
            image = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)
        

        # Process the image through YOLOv8
        with tracer.start_span("vision_yolov8_model_inference", context=process_request_context) as inference_span:
            results = model(image)[0]

        # Post-process the results
        with tracer.start_span("vision_yolov8_model_post_processing", context=process_request_context) as post_processing_span:
            image = results.plot(boxes=True, labels=True, line_width=3, conf=True, probs=False)  # plot a BGR numpy array of predictions

            # Convert the image to a binary string
            image_data = cv2.imencode('.png', image)[1].tobytes()

        # Add context to the span in response headers
        with tracer.start_span("vision_yolov8_model_insert_tracing_header", context=process_request_context) as insert_tracing_header_span:
            headers = {}
            context = baggage.set_baggage("context", "vision-microservice-yolov8")
            W3CBaggagePropagator().inject(context, headers)
            TraceContextTextMapPropagator().inject(headers, context)

        return Response(image_data, mimetype='image/png', headers=headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)