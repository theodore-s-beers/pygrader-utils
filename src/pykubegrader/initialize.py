import json
import os

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
        return

    jhub_user = os.getenv("JUPYTERHUB_USER")
    if jhub_user is None:
        print("Setup unsuccessful. Are you on JupyterHub?")
        return

    pn.extension(silent=True)

    try:
        responses = update_responses(key="assignment", value=name)

        seed = responses.get("seed")
        if seed is None:
            new_seed = hash(jhub_user) % 1000
            responses = update_responses(key="seed", value=new_seed)
    except (TypeError, json.JSONDecodeError) as e:
        print(f"Failed to initialize assignment: {e}")
        return

    print("Assignment successfully initialized")
    print(f"Assignment: {name}")
    print(f"Username: {jhub_user}")
