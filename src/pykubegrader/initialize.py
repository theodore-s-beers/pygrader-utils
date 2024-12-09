import panel as pn
from IPython import get_ipython

# Initialize Panel extension
pn.extension()

# Import your telemetry
try:
    from pykubegrader.telemetry import telemetry
except ImportError:
    telemetry = None
    print("Telemetry module not found. Ensure it is installed and accessible.")

# Check if in a Jupyter environment and set up pre-run event
ipython = get_ipython()
if ipython and telemetry:
    ipython.events.register("pre_run_cell", telemetry)
    print("Telemetry registered with pre_run_cell event.")
else:
    print("Not in a Jupyter environment or telemetry unavailable.")
