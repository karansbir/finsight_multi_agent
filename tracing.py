import os
from phoenix.otel import register

# Set these in your .env or here directly
os.environ["PHOENIX_API_KEY"] = os.getenv("PHOENIX_API_KEY", "YOUR_API_KEY")
os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "YOUR_COLLECTOR_ENDPOINT")

tracer_provider = register(
    project_name="finsight-agent",
    auto_instrument=True,
    set_global_tracer_provider=False,  # Do not override global tracer
)

tracer = tracer_provider.get_tracer(__name__) 