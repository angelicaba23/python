from fastapi import FastAPI
from dotenv import load_dotenv
import os
import logging

from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Set up OpenTelemetry tracing and logging
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

logger_provider = LoggerProvider(
    resource=Resource.create({
        "service.name": "my_fastapi_service",
        "service.instance.id": "instance-1",
    })
)
set_logger_provider(logger_provider)

exporter = OTLPLogExporter(insecure=True)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)

# Attach OTLP handler to root logger
logging.getLogger().addHandler(handler)

# Create different namespaced loggers
logger1 = logging.getLogger("myapp.area1")
logger2 = logging.getLogger("myapp.area2")

# Define FastAPI routes
@app.get("/")
def read_root():
    logger1.info("Root endpoint was called")
    return {"message": "Hello, World!"}

@app.get("/greet/{name}")
def greet(name: str):
    logger2.info(f"Greet endpoint was called with name: {name}")
    return {"message": f"Hello, {name}!"}

# Example of trace context correlation
tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("example_span"):
    logger2.error("This is an error message within a trace span")

# Shutdown logger provider on application exit
@app.on_event("shutdown")
def shutdown_event():
    logger_provider.shutdown()