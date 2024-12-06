import random
from typing import Tuple

import panel as pn


def list_of_lists(options: list) -> bool:
    return all(isinstance(elem, list) for elem in options)


def shuffle_options(options, seed: int):
    random.seed(seed)
    random.shuffle(options)

    return options


def shuffle_questions(
    desc_widgets: list[pn.pane.HTML],
    dropdowns: list[pn.widgets.Select] | list[pn.Column],
    seed: int,
) -> list[Tuple[pn.pane.HTML, pn.widgets.Select | pn.Column]]:
    random.seed(seed)

    # Combine widgets into pairs
    widget_pairs = list(zip(desc_widgets, dropdowns))

    random.shuffle(widget_pairs)
    return widget_pairs
