import os
import re
import socket

import numpy as np
import panel as pn

from .telemetry import ensure_responses, update_responses
from pygrader_utils.info_widget import StudentInfoForm

# TODO: make not hardcoded as Drexel-specific
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
    """
    A form for collecting student information using Panel widgets.
    Attributes:
        first_name (str): The first name of the student.
        last_name (str): The last name of the student.
        drexel_id (str): The Drexel ID of the student.
        drexel_email (str): The Drexel email of the student.
        hostname (str): The hostname of the machine.
        ip_address (str): The IP address of the machine.
        jupyter_user (str): The JupyterHub user.
        seed (int): A random seed value.
        first_name_widget (pn.widgets.TextInput): Widget for inputting the first name.
        last_name_widget (pn.widgets.TextInput): Widget for inputting the last name.
        drexel_id_widget (pn.widgets.TextInput): Widget for inputting the Drexel ID.
        drexel_email_widget (pn.widgets.TextInput): Widget for inputting the Drexel email.
        submit_button (pn.widgets.Button): Button to submit the form.
        message (pn.pane.Str): Pane to display status messages.
        layout (pn.Column): Layout of the form.
    Methods:
        __init__(**kwargs): Initializes the form with optional keyword arguments.
        submit(_): Handles the form submission, validates input, and updates responses.
        show(): Returns the layout of the form for display.
        
    Usage Example:
        # Create an instance of the form
        form = StudentInfoForm()
        # Display the form
        pn.serve(form.show())
    """
    
    def __init__(self, **kwargs) -> None:
        """
        Initializes the InfoWidget with optional keyword arguments.

        Keyword Args:
            first_name (str): The first name of the user. Defaults to an empty string.
            last_name (str): The last name of the user. Defaults to an empty string.
            drexel_id (str): The Drexel ID of the user. Defaults to an empty string.
            drexel_email (str): The Drexel email of the user. Defaults to an empty string.
            hostname (str): The hostname of the user's machine. Defaults to an empty string.
            ip_address (str): The IP address of the user's machine. Defaults to an empty string.
            jupyter_user (str): The Jupyter username of the user. Defaults to an empty string.
            seed (int): A random seed value. Defaults to a random integer between 0 and 100.

        Attributes:
            first_name_widget (pn.widgets.TextInput): Widget for inputting the first name.
            last_name_widget (pn.widgets.TextInput): Widget for inputting the last name.
            drexel_id_widget (pn.widgets.TextInput): Widget for inputting the Drexel ID.
            drexel_email_widget (pn.widgets.TextInput): Widget for inputting the Drexel email.
            submit_button (pn.widgets.Button): Button to submit the form.
            message (pn.pane.Str): Placeholder for status message.
            layout (pn.Column): Layout of the form.
        """
        
        self.first_name = kwargs.get("first_name", "")
        self.last_name = kwargs.get("last_name", "")
        self.drexel_id = kwargs.get("drexel_id", "")
        self.drexel_email = kwargs.get("drexel_email", "")
        self.hostname = kwargs.get("hostname", "")
        self.ip_address = kwargs.get("ip_address", "")
        self.jupyter_user = kwargs.get("jupyter_user", "")
        self.seed = kwargs.get("seed", np.random.randint(0, 100))

        self.first_name_widget = pn.widgets.TextInput(
            name="First Name", value=self.first_name
        )
        self.last_name_widget = pn.widgets.TextInput(
            name="Last Name", value=self.last_name
        )
        self.drexel_id_widget = pn.widgets.TextInput(
            name="Drexel ID", value=self.drexel_id
        )
        self.drexel_email_widget = pn.widgets.TextInput(
            name="Drexel Email", value=self.drexel_email
        )

        self.submit_button = pn.widgets.Button(
            name="Submit", button_type="primary", styles=dict(margin_top="1.5em")
        )
        self.submit_button.on_click(self.submit)

        self.message = pn.pane.Str("")  # Placeholder for status message

        self.layout = pn.Column(
            "# Student Information Form",
            self.first_name_widget,
            self.last_name_widget,
            self.drexel_id_widget,
            self.drexel_email_widget,
            self.submit_button,
            self.message,
        )

    def submit(self, _) -> None:
        """
        Handles the submission of user information from widgets, validates the input,
        and updates the responses. Displays a success or error message based on the validation results.

        Args:
            _ (Any): Placeholder argument, not used in the function.

        Raises:
            ValueError: If any required form input is missing, the email format is invalid,
                or the Drexel ID does not match the email prefix.

        Notes:
            - The function ensures that all required fields are filled.
            - It validates the email format and checks if the Drexel ID matches the email prefix.
            - It updates the responses with the provided information.
            - Displays a success message if all validations pass, otherwise displays an error message.
        """
        # Ensure responses dictionary is initialized
        info = ensure_responses()

        # Collect and strip input values from widgets
        info["first_name"] = self.first_name_widget.value.strip()
        info["last_name"] = self.last_name_widget.value.strip()
        info["drexel_id"] = self.drexel_id_widget.value.strip()
        info["drexel_email"] = self.drexel_email_widget.value.strip()

        # Get hostname and JupyterHub user
        info["hostname"] = socket.gethostname()
        info["jupyter_user"] = os.environ.get("JUPYTERHUB_USER", "Not on JupyterHub")

        # Generate a random seed if not already present
        if "seed" not in info:
            info["seed"] = np.random.randint(0, 100)

        # Attempt to get the IP address of the hostname
        try:
            info["ip_address"] = socket.gethostbyname(info["hostname"])
        except socket.gaierror:
            info["ip_address"] = "IP unavailable"

        try:
            # Validate that all required fields are filled
            for key in KEYS:
            if info[key] == "":
                raise ValueError(f"Missing form input: {key}")

            # Validate the email format
            if not EMAIL_PATTERN.fullmatch(info["drexel_email"]):
            raise ValueError(f"Invalid email format: {info['drexel_email']}")

            # Ensure Drexel ID matches the email prefix
            email_prefix = info["drexel_email"].split("@")[0]
            if info["drexel_id"] != email_prefix:
            raise ValueError(
                f"Drexel ID {info['drexel_id']} does not match email {info['drexel_email']}"
            )

            # Update responses with validated information
            for key in KEYS:
            update_responses(key, info[key])

            # Display success message
            self.message.object = "Student info recorded successfully!"
            self.message.style = {"color": "green"}
        except ValueError as e:
            # Display error message if validation fails
            self.message.object = str(e)
            self.message.style = {"color": "red"}

    def show(self):
        """
        Displays the layout of the widget.

        Returns:
            The layout of the widget.
        """
        return self.layout
