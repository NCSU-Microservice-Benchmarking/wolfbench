import requests
import json

import os

from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry import trace, propagators, baggage
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor

jaeger_endpoint = os.getenv("JAEGER_ENDPOINT", "http://localhost:4318")

# setup opentelemetry
resource = Resource(
    attributes={
        SERVICE_NAME: "vision-microservice-test"
    }
)


trace_provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=jaeger_endpoint + "/v1/traces"))
trace_provider.add_span_processor(processor)
trace.set_tracer_provider(trace_provider)

tracer = trace.get_tracer(__name__)

if __name__ == "__main__":
    
    host = "http://127.0.0.1:5000"

    with tracer.start_as_current_span("test") as test_root_span:
        test_context = baggage.set_baggage("context", "test")
        # send a get request to the greet endpoint
        with tracer.start_span("test_greet", context=test_context) as greet_span:
            response = requests.get(host+"/greet")
            # print the response text
            print(response.text)
        with tracer.start_span("test_inference", context=test_context) as detections_span:
            # set context and insert into header
            detection_context = baggage.set_baggage("context", "test_inference")
            headers = {}
            W3CBaggagePropagator().inject(headers, detection_context)
            TraceContextTextMapPropagator().inject(headers, detection_context)
            # encode the image as a binary string
            image = open("bus.png","rb").read()
            # put the image in a multipart/form-data
            files = {'image': image}
            # send a post request to the detect endpoint
            response = requests.post(host + '/', files=files, headers=headers)
            # response = requests.post(host + '/', files=files)
            #response = requests.post(host+"/model-hog-people", "")
            # check the response status code
            print(response.status_code)
            # save the image
            open("result.png","wb").write(response.content)