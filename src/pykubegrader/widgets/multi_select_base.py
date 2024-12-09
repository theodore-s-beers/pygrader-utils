from typing import Callable, Tuple

import panel as pn

from .misc import shuffle_questions
from .telemetry import ensure_responses, update_responses


class MultiSelectQuestion:
    def __init__(
        self,
        title: str,
        style: Callable[
            [list[str], list[list[str]], list[bool]],
            Tuple[list[pn.pane.HTML], list[pn.Column]],
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

        self.submit_button = pn.widgets.Button(name="Submit")
        self.submit_button.on_click(self.submit)

        widget_pairs = shuffle_questions(description_widgets, self.widgets, seed)

        # Panel layout
        question_header = pn.pane.HTML(
            f"<h2>Question {self.question_number}: {title}</h2>"
        )
        question_body = pn.Column(
            *[
                pn.Row(desc_widget, checkbox_set)
                for desc_widget, checkbox_set in widget_pairs
            ]
        )

        self.layout = pn.Column(question_header, question_body, self.submit_button)

    def submit(self, _) -> None:
        responses_flat: list[bool] = []
        self.responses_nested: list[list[bool]] = []

        for row in self.widgets:
            next_selections = []

            for widget in row.objects:
                # Skip HTML widgets
                if isinstance(widget, pn.pane.HTML):
                    continue

                if isinstance(widget, pn.widgets.Checkbox):
                    next_selections.append(widget.value)
                    responses_flat.append(widget.value)  # For flat list of responses

            # Append all responses for this widget at once, forming a list of lists
            self.responses_nested.append(next_selections)

        self.record_responses(responses_flat)

    def record_responses(self, responses_flat: list[bool]) -> None:
        for key, value in zip(self.keys, responses_flat):
            update_responses(key, value)

        print("Responses recorded successfully")

    def show(self):
        return self.layout
