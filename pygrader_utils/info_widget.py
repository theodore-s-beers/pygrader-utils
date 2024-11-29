import os
import re
import socket

import ipywidgets  # type: ignore[import-untyped]
import numpy as np
from IPython.display import display

from .telemetry import ensure_responses, update_responses

EMAIL_PATTERN = re.compile(r"[a-z]+\d+@drexel\.edu")

KEYS = [
    "first_name",
    "last_name",
    "drexel_id",
    "drexel_email",
    "hostname",
    "ip_address",
    "jupyter_user",
    "seed",
]


class StudentInfoForm:
    def __init__(self, **kwargs) -> None:
        self.first_name = kwargs.get("first_name", "")
        self.last_name = kwargs.get("last_name", "")
        self.drexel_id = kwargs.get("drexel_id", "")
        self.drexel_email = kwargs.get("drexel_email", "")
        self.hostname = kwargs.get("hostname", "")
        self.ip_address = kwargs.get("ip_address", "")
        self.jupyter_user = kwargs.get("jupyter_user", "")
        self.seed = kwargs.get("seed", np.random.randint(0, 100))

        self.first_name_widget = ipywidgets.Text(
            description="First Name:", value=self.first_name
        )
        self.last_name_widget = ipywidgets.Text(
            description="Last Name:", value=self.last_name
        )
        self.drexel_id_widget = ipywidgets.Text(
            description="Drexel ID:", value=self.drexel_id
        )
        self.drexel_email_widget = ipywidgets.Text(
            description="Drexel Email:", value=self.drexel_email
        )

        self.submit_button = ipywidgets.Button(description="Submit")
        self.submit_button.on_click(self.submit)

        display(
            self.first_name_widget,
            self.last_name_widget,
            self.drexel_id_widget,
            self.drexel_email_widget,
            self.submit_button,
        )

    def submit(self, _) -> None:
        info = ensure_responses()

        info["first_name"] = self.first_name_widget.value.strip()
        info["last_name"] = self.last_name_widget.value.strip()
        info["drexel_id"] = self.drexel_id_widget.value.strip()
        info["drexel_email"] = self.drexel_email_widget.value.strip()

        info["hostname"] = socket.gethostname()
        info["jupyter_user"] = os.environ.get("JUPYTERHUB_USER", "Not on JupyterHub")

        if "seed" not in info:
            info["seed"] = np.random.randint(0, 100)

        try:
            info["ip_address"] = socket.gethostbyname(info["hostname"])
        except socket.gaierror:
            info["ip_address"] = "IP unavailable"

        for key in KEYS:
            if info[key] == "":
                raise ValueError(f"Missing form input: {key}")

        if not EMAIL_PATTERN.fullmatch(info["drexel_email"]):
            raise ValueError(f"Invalid email format: {info['drexel_email']}")

        email_prefix = info["drexel_email"].split("@")[0]
        if info["drexel_id"] != email_prefix:
            raise ValueError(
                f"Drexel ID {info['drexel_id']} does not match email {info['drexel_email']}"
            )

        for key in KEYS:
            update_responses(key, info[key])

        print("Student info recorded successfully")
