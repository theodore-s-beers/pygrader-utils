import ipywidgets as widgets  # type: ignore[import-untyped]

from .multi_select_base import MultiSelectQuestion


def MultiSelect(
    descriptions: list[str], options: list[list[str]], initial_vals: list[bool]
):
    desc_widgets: list[widgets.HTML] = []
    checkboxes: list[widgets.VBox] = []

    # Create a separator line between questions
    separator = widgets.HTML(
        value="<hr style='border:1px solid lightgray; width:100%;'>"
    )

    i = 0

    for question, option_set in zip(descriptions, options):
        desc_width = "500px"

        desc_widget = widgets.HTML(
            value=f"<hr style='border:1px solid lightgray; width:100%;'><div style='text-align: left; width: {desc_width};'><b>{question}</b></div>"
        )

        checkbox_set = []

        for option in option_set:
            checkbox_set.append(
                widgets.Checkbox(
                    value=initial_vals[i],
                    description=option,
                    disabled=False,
                    indent=False,
                    layout={"width": "auto", "wrap": "auto"},
                )
            )

            i += 1

        desc_widgets.append(desc_widget)
        checkboxes.append(widgets.VBox([separator] + checkbox_set))

    return desc_widgets, checkboxes


class SelectMany(MultiSelectQuestion):
    def __init__(
        self,
        title="Select all statements which are TRUE",
        style=MultiSelect,
        question_number=3,
        keys=["MS1", "MS2", "MS3", "MS4", "MS5"],
        options=[
            ["`if` statements", "`for` loops", "`while` loops", "`end` statements"],
            ["dictionary", "tuple", "float", "class"],
            [
                "A class can inherit attributes and methods from another class.",
                "The `self` keyword is used to access variables that belong to a class.",
                "`__init__` runs on instantiation of a class.",
                "Variables assigned in a class are always globally accessible.",
            ],
            [
                "Keys in dictionaries are mutable.",
                "It is possible to store a list of dictionaries in Python.",
                "You can create multiple instances of a class with different values.",
                "If `list1` is a list and you assign it to `list2` and append a value to `list2`, `list1` will also contain the value that was appended to `list2`.",
            ],
            [
                "In `print(i)`, `i` must be a string.",
                "`2day` is not a valid variable name.",
                "`i` is not defined when evaluating the `while` loop.",
                "`i < 5` is not valid syntax to compare a variable `i` to an integer `5`, if `i` is a float.",
            ],
        ],
        descriptions=[
            "Which of the following control structures are used in Python? (Select all that apply)",
            "Which of the following are built-in data structures in Python? (Select all that apply)",
            "Concerning object-oriented programming in Python, which of the following statements are true? (Select all that apply)",
            "Select all of the TRUE statements",
            """
            Select all the syntax errors in the following code:
            <pre>
                <code class="language-python">
                    2day = 'Tuesday'
                    while i < 5:
                        print(i)
                        i += 1.0
                </code>
            </pre>
            """,
        ],
        points=1,
    ):
        super().__init__(
            title=title,
            style=style,
            question_number=question_number,
            keys=keys,
            options=options,
            descriptions=descriptions,
            points=points,
        )
