from typing import Callable, Tuple

import panel as pn

from .misc import shuffle_questions
from .telemetry import ensure_responses, update_responses


class SelectQuestion:
    def __init__(
        self,
        title: str,
        style: Callable[
            [list[str], list, list[str]],
            Tuple[list[pn.pane.HTML], list[pn.widgets.Select]],
        ],
        question_number: int,
        keys: list[str],
        options: list,
        descriptions: list[str],
        points: int,
    ):
        responses = ensure_responses()

        self.points = points
        self.question_number = question_number
        self.keys = keys
        self.style = style

        try:
            seed: int = responses["seed"]
        except ValueError:
            raise ValueError(
                "You must submit your student info before starting the exam"
            )

        # Dynamically assigning attributes based on keys, with default values from responses
        for key in self.keys:
            setattr(self, key, responses.get(key, None))

        self.initial_vals: list = [getattr(self, key) for key in self.keys]

        desc_widgets, self.widgets = style(descriptions, options, self.initial_vals)

        self.submit_button = pn.widgets.Button(name="Submit", button_type="primary")
        self.submit_button.on_click(self.submit)

        widget_pairs = shuffle_questions(desc_widgets, self.widgets, seed)

        self.layout = pn.Column(
            f"# Question {self.question_number}: {title}",
            *(pn.Column(desc_widget, pn.Row(dropdown)) for desc_widget, dropdown in widget_pairs),
            self.submit_button,
        )

    def submit(self, _) -> None:
        selections = {key: widget.value for key, widget in zip(self.keys, self.widgets)}

        for value in selections.values():
            if value is None:
                raise ValueError("Please answer all questions before submitting")

        for key, value in selections.items():
            update_responses(key, value)

        print("Responses recorded successfully")

    def show(self):
        return self.layout
