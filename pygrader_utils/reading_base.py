import copy
from typing import Optional

import ipywidgets as widgets  # type: ignore[import-untyped]
from IPython.display import display

from .misc import shuffle_options
from .telemetry import ensure_responses, update_responses


class ReadingPython:
    def __init__(
        self,
        title: str,
        question_number: int,
        options: dict,
    ) -> None:
        # Load responses from JSON (or create file if it doesn't exist)
        responses = ensure_responses()

        self.question_number = question_number

        default = None

        # Dynamically assign attributes based on keys, with default values from responses
        for num in range(len(options["lines_to_comment"]) + options["n_rows"]):
            key = f"q{question_number}_{num+1}"

            # Dynamically assign the value from the responses file for persistence
            if num < len(options["lines_to_comment"]):
                setattr(self, key, responses.get(key, default))
            else:
                setattr(
                    self,
                    key,
                    responses.get(key, [default] * (len(options["table_headers"]) - 1)),
                )

        # Checks that a seed was assigned to responses
        try:
            seed: int = responses["seed"]
        except ValueError:
            raise ValueError(
                "You must submit your student info before starting the exam"
            )

        #
        # Question title
        #

        display(widgets.HTML(f"<h2>Question {question_number}: {title}</h2>"))

        #
        # Comment dropdowns
        #

        self.dropdowns_for_comments: dict[str, widgets.Dropdown] = {
            line: widgets.Dropdown(
                options=shuffle_options(options["comments_options"], seed),
                description=f"Line {line}:",
                layout=widgets.Layout(width="600px"),
                value=getattr(self, f"q{question_number}_{i_comments+1}"),
            )
            for i_comments, line in enumerate(options["lines_to_comment"])
        }

        for dropdown in self.dropdowns_for_comments.values():
            display(dropdown)

        #
        # Execution dropdowns
        #

        # Instructions
        execution_instructions = widgets.HTML(
            value="""
                <h3>For each step, select the appropriate response:</h3>
            """
        )

        # Header row
        header_row = widgets.HBox(
            [
                widgets.HTML(
                    value=f"<strong>{header}</strong>",
                    layout=widgets.Layout(width="150px"),
                )
                for header in options["table_headers"]
            ],
            layout=widgets.Layout(display="flex", justify_content="center"),
        )

        # Make a deep copy of the lines to comment and add a null value to the beginning
        # This is to provide the null response to the question
        line_comment: list[int | str] = copy.deepcopy(options["lines_to_comment"])
        line_comment.insert(0, "")

        dropdown_options = [
            line_comment,
            options["variables_changed"],
            options["current_values"],
            options["datatypes"],
        ]

        # Function to create a row with dropdowns
        def create_row(step: int) -> widgets.HBox:
            widgets_list: list[widgets.HTML | widgets.Dropdown] = []

            for i in range(len(options["table_headers"])):
                if i == 0:
                    # If it's the first column, create an HTML label widget with the step number
                    widgets_list.append(
                        widgets.HTML(
                            value=f"Step {step+1}", layout=widgets.Layout(width="150px")
                        )
                    )
                else:
                    # If not the first column, create a Dropdown widget
                    # Set options from dropdown_options, indexed by i-1
                    widgets_list.append(
                        widgets.Dropdown(
                            layout=widgets.Layout(width="150px"),
                            options=dropdown_options[i - 1],
                            value=getattr(
                                self,
                                f'q{question_number}_{len(options["lines_to_comment"])+step+1}',
                            )[i - 1],
                        )
                    )

            # Return an HBox widget containing the list of widgets, horizontally aligned
            return widgets.HBox(
                widgets_list,
                layout=widgets.Layout(display="flex", justify_content="center"),
            )

        # Generate rows dynamically based on n_rows
        self.rows = [create_row(step) for step in range(options["n_rows"])]

        # Combine header and rows
        execution_steps = [header_row] + self.rows

        # Display section 2
        display(execution_instructions, *execution_steps)

        # Submit button
        self.submit_button = widgets.Button(description="Submit")
        self.submit_button.on_click(self.submit)

        display(self.submit_button)

    def submit(self, _) -> None:
        # Get section 1 responses
        self.output_comments: list[str] = []
        for out in self.dropdowns_for_comments.values():
            self.output_comments.append(out.value if isinstance(out.value, str) else "")

        # Get section 2 responses
        self.output_execution: list[list[Optional[str | int]]] = []

        for row in self.rows[:]:
            row_value: list[Optional[str | int]] = []

            for box in row.children:
                if isinstance(box, widgets.Dropdown):
                    row_value.append(box.value)

            if not any(row_value):
                continue

            self.output_execution.append(row_value)

        # Persist responses to JSON
        i = 0
        for comment_val in self.output_comments:
            i += 1
            update_responses(f"q{self.question_number}_{i}", comment_val)

        for exec_val in self.output_execution:
            i += 1
            update_responses(f"q{self.question_number}_{i}", exec_val)

        print("Responses recorded successfully")
