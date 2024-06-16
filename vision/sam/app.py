from ultralytics import SAM
from flask import Flask, request, Response
import torch
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
model = SAM('sam_b.pt')

# Initialize the model
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)