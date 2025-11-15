from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
import os
import logging

def init_tracing():
    OTEL_COLLECTOR_ENDPOINT =\
        (f"{os.getenv("OPENTELEMTRY_HOST", "http://opentelemetry-collector.default.svc.cluster.local")}"
         f":{os.getenv("OPENTELEMTRY_PORT", "4318")}/v1/traces")
    logger = logging.getLogger()
    logger.info(f"Sending telemetry to {OTEL_COLLECTOR_ENDPOINT}")

    resource = Resource.create({
        "service.name": "crypto-price-service"
    })
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    otlp_exporter = OTLPSpanExporter(endpoint=OTEL_COLLECTOR_ENDPOINT)

    processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(processor)

    # Auto instrumentation for http requests
    RequestsInstrumentor().instrument()

    return trace.get_tracer("crypto-tracer")

