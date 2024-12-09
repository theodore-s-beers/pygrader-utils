import panel as pn
from IPython import get_ipython

from .telemetry import telemetry

# Check if in a Jupyter environment
ipython = get_ipython()

if ipython is not None:
    # Initialize Panel extension
    pn.extension()

    # Register telemetry with pre_run_cell event
    ipython.events.register("pre_run_cell", telemetry)

    print("Setup completed successfully")
else:
    print("Setup unsuccessful. Are you in a Jupyter environment?")
