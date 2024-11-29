from typing import Tuple

import ipywidgets as widgets  # type: ignore[import-untyped]

from .misc import list_of_lists
from .select_base import SelectQuestion


def MultipleChoice(
    descriptions: list[str],
    options: list[str] | list[list[str]],
    initial_vals: list[str],
) -> Tuple[list[widgets.HTML], list[widgets.Dropdown]]:
    desc_width = "350px"

    desc_widgets = [
        widgets.HTML(
            value=f"<div style='text-align: left; width: {desc_width};'><b>{desc}</b></div>"
        )
        for desc in descriptions
    ]

    dropdowns = [
        widgets.Dropdown(
            options=option, value=value, layout=widgets.Layout(width="300px")
        )
        for value, option in zip(
            initial_vals,
            options if list_of_lists(options) else [options] * len(initial_vals),
        )
    ]

    return desc_widgets, dropdowns


class TypesQuestion(SelectQuestion):
    def __init__(
        self,
        title="Select the option that matches the definition:",
        style=MultipleChoice,
        question_number=1,
        keys=["types1", "types2", "types3", "types4", "types5", "types6"],
        options=[
            "None",
            "list",
            "function",
            "dictionary",
            "array",
            "variable",
            "integer",
            "string",
            "tuple",
            "iterator",
            "float",
            "object",
            "class",
            "module",
            "package",
            "instance",
        ],
        descriptions=[
            "An ordered, mutable collection of items, defined with []",
            "A file containing Python definitions and statements.",
            "Collection of elements of the same type, which allows for efficient storage and manipulation of sequences of data",
            "an immutable and ordered collection of elements in Python, which can contain mixed data types",
            "A sequence of Unicode characters.",
            "A data type that represents real numbers with a decimal point.",
        ],
        points=3,
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
