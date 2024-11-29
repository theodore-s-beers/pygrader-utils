from typing import Callable, Tuple

import ipywidgets as widgets  # type: ignore[import-untyped]
from IPython.display import display

from .misc import shuffle_questions
from .telemetry import ensure_responses, update_responses


class MultiSelectQuestion:
    def __init__(
        self,
        title: str,
        style: Callable[
            [list[str], list[list[str]], list[bool]],
            Tuple[list[widgets.HTML], list[widgets.VBox]],
        ],
        question_number: int,
        keys: list[str],
        options: list[list[str]],
        descriptions: list[str],
        points: int,
    ):
        responses = ensure_responses()

        self.points = points
        self.question_number = question_number
        self.style = style

        flat_index = 0
        self.keys: list[str] = []
        for i, _ in enumerate(keys):
            for _ in options[i]:
                flat_index += 1  # Start at 1
                self.keys.append(f"q{question_number}_{flat_index}")

        try:
            seed: int = responses["seed"]
        except ValueError:
            raise ValueError(
                "You must submit your student info before starting the exam"
            )

        # Dynamically assigning attributes based on keys, with default values from responses
        for key in self.keys:
            setattr(self, key, responses.get(key, False))

        self.initial_vals = [getattr(self, key) for key in self.keys]

        description_widgets, self.widgets = style(
            descriptions, options, self.initial_vals
        )

        self.submit_button = widgets.Button(description="Submit")
        self.submit_button.on_click(self.submit)

        widget_pairs = shuffle_questions(description_widgets, self.widgets, seed)

        display(widgets.HTML(f"<h2>Question {self.question_number}: {title}</h2>"))

        # Display the widgets using HBox for alignment
        for desc_widget, checkbox_set in widget_pairs:
            display(widgets.HBox([desc_widget, checkbox_set]))

        display(self.submit_button)

    def submit(self, _) -> None:
        responses_flat: list[bool] = []
        self.responses_nested: list[list[bool]] = []

        for row in self.widgets:
            next_selections = []

            for widget in row.children:
                # Skip HTML widgets
                if isinstance(widget, widgets.HTML):
                    continue

                if isinstance(widget, widgets.Checkbox):
                    next_selections.append(widget.value)
                    responses_flat.append(widget.value)  # For flat list of responses

            # Append all responses for this widget at once, forming a list of lists
            self.responses_nested.append(next_selections)

        self.record_responses(responses_flat)

    def record_responses(self, responses_flat: list[bool]) -> None:
        for key, value in zip(self.keys, responses_flat):
            update_responses(key, value)

        print("Responses recorded successfully")
