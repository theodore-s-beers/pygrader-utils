import random
from typing import Tuple

import ipywidgets as widgets  # type: ignore[import-untyped]


def list_of_lists(options: list) -> bool:
    return all(isinstance(elem, list) for elem in options)


def shuffle_options(options, seed: int):
    random.seed(seed)
    random.shuffle(options)

    return options


def shuffle_questions(
    desc_widgets: list[widgets.HTML],
    dropdowns: list[widgets.Dropdown] | list[widgets.VBox],
    seed: int,
) -> list[Tuple[widgets.HTML, widgets.Dropdown | widgets.VBox]]:
    random.seed(seed)

    # Combine widgets into pairs
    widget_pairs = list(zip(desc_widgets, dropdowns))

    random.shuffle(widget_pairs)
    return widget_pairs
