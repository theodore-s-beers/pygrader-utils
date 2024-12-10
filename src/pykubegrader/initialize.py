import json

import panel as pn
from IPython import get_ipython

from .telemetry import telemetry, update_responses


def initialize_assignment(name: str) -> None:
    ipython = get_ipython()
    if ipython is None:
        print("Setup unsuccessful. Are you in a Jupyter environment?")
        return

    try:
        ipython.events.register("pre_run_cell", telemetry)
    except TypeError as e:
        print(f"Failed to register telemetry: {e}")

    pn.extension()

    try:
        update_responses(key="assignment", value=name)
    except (TypeError, json.JSONDecodeError) as e:
        print(f"Failed to initialize assignment: {e}")
        return

    print("Assignment successfully initialized")
