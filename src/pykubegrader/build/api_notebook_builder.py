from dataclasses import dataclass
from pathlib import Path
import json
import nbformat
import json
import re


@dataclass
class FastAPINotebookBuilder:
    notebook_path: str

    def __post_init__(self):
        self.root_path, self.filename = FastAPINotebookBuilder.get_filename_and_root(
            self.notebook_path
        )

        self.import_cell = self.extract_first_cell()
        self.import_cell = self.add_imports()

        self.assertion_tests = self.question_dict()

    def add_imports(
        self, import_text="from pykubegrader.initialize import initialize_assignment"
    ):
        """
        Adds the necessary imports to the first cell of the notebook.
        """

        lines = self.import_cell["source"]
        last_import_index = -1

        # Find the index of the last 'import' line
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if stripped_line.startswith("import") or stripped_line.startswith("from"):
                last_import_index = i

        # Insert the new import line after the last import
        if last_import_index != -1:
            lines.insert(last_import_index + 1, import_text)
        else:
            # If no import is found, add the new import line at the top
            lines.insert(0, import_text)

        # adds the initialize assignment line
        lines.append(f'responses = initialize_assignment("{self.filename}")')
        lines = [line.replace("\n", "") for line in lines]

        return "\n".join(lines)

    def extract_first_cell(self):
        with open(self.notebook_path, "r", encoding="utf-8") as f:
            notebook = json.load(f)
        if "cells" in notebook and len(notebook["cells"]) > 0:
            return notebook["cells"][0]
        else:
            return None

    @staticmethod
    def get_filename_and_root(path):
        path_obj = Path(path).resolve()  # Resolve the path to get an absolute path
        root_path = path_obj.parent  # Get the parent directory
        filename = path_obj.name  # Get the filename
        return root_path, filename

    def get_cell(self, cell_index):
        with open(self.notebook_path, "r", encoding="utf-8") as f:
            notebook = json.load(f)
        if "cells" in notebook and len(notebook["cells"]) > cell_index:
            return notebook["cells"][cell_index]
        else:
            return None

    def replace_cell_source(self, cell_index, new_source, output_path=None):
        """
        Replace the source code of a specific Jupyter notebook cell.

        Args:
            cell_index (int): Index of the cell to be modified (0-based).
            new_source (str): New source code to replace the cell's content.
            output_path (str): Path to save the modified notebook (default is to overwrite the original).
        """
        # Load the notebook
        with open(self.notebook_path, "r", encoding="utf-8") as f:
            notebook = nbformat.read(f, as_version=4)

        # Check if the cell index is valid
        if cell_index >= len(notebook.cells) or cell_index < 0:
            raise IndexError(
                f"Cell index {cell_index} is out of range for this notebook."
            )

        # Replace the source code of the specified cell
        notebook.cells[cell_index]["source"] = new_source

        # Save the notebook
        output_path = (
            output_path or self.notebook_path
        )  # Overwrite original if no output path is provided
        with open(output_path, "w", encoding="utf-8") as f:
            nbformat.write(notebook, f)
        print(f"Updated notebook saved to {output_path}")

    @staticmethod
    def extract_log_variables(cell):
        """Extracts log variables from the first cell."""
        if "source" in cell:
            for line in cell["source"]:
                # Look for the log_variables pattern
                match = re.search(r"log_variables:\s*\[(.*?)\]", line)
                if match:
                    # Split the variables by comma and strip whitespace
                    log_variables = [var.strip() for var in match.group(1).split(",")]
                    return log_variables
        return []

    def tag_questions(cells_dict):
        """
        Adds 'is_first' and 'is_last' boolean flags to the cells based on their position
        within the group of the same question. All cells will have both flags.

        Args:
            cells_dict (dict): A dictionary where keys are cell IDs and values are cell details.

        Returns:
            dict: The modified dictionary with 'is_first' and 'is_last' flags added.
        """
        if not isinstance(cells_dict, dict):
            raise ValueError("Input must be a dictionary.")

        # Ensure all cells have the expected structure
        for key, cell in cells_dict.items():
            if not isinstance(cell, dict):
                raise ValueError(f"Cell {key} is not a dictionary.")
            if "question" not in cell:
                raise KeyError(f"Cell {key} is missing the 'question' key.")

        # Group the keys by question name
        question_groups = {}
        for key, cell in cells_dict.items():
            question = cell.get(
                "question"
            )  # Use .get() to avoid errors if key is missing
            if question not in question_groups:
                question_groups[question] = []
            question_groups[question].append(key)

        # Add 'is_first' and 'is_last' flags to all cells
        for question, keys in question_groups.items():
            for i, key in enumerate(keys):
                cells_dict[key]["is_first"] = i == 0
                cells_dict[key]["is_last"] = i == len(keys) - 1

        return cells_dict

    def question_dict(self):
        """
        Extracts all logical conditions from `assert` statements in Jupyter notebook cells
        that start with ''''# BEGIN TEST CONFIG'. Also extracts the first line containing `points:`
        and adds the points value to the dictionary.

        Returns:
            dict: A dictionary where keys are cell indices and values are dictionaries containing:
                - "assertions": A list of logical conditions extracted from assert statements.
                - "points": The points value extracted from the first `points:` line.
        """

        # Read the notebook file
        notebook_path = Path(self.notebook_path)
        if not notebook_path.exists():
            raise FileNotFoundError(f"The file {notebook_path} does not exist.")

        with open(notebook_path, "r", encoding="utf-8") as f:
            notebook = json.load(f)

        # Initialize the dictionary to store conditions and points
        results_dict = {}

        # Iterate through the cells in the notebook
        for cell_index, cell in enumerate(notebook.get("cells", [])):
            if cell.get("cell_type") == "raw":
                source = "".join(
                    cell.get("source", "")
                )  # Join the cell source as a string
                if source.strip().startswith("# BEGIN QUESTION"):
                    question_name = re.search(r"name:\s*(.*)", source)
                    question_name = (
                        question_name.group(1).strip() if question_name else None
                    )
            elif cell.get("cell_type") == "code":
                source = "".join(
                    cell.get("source", "")
                )  # Join the cell source as a string

                # Check if the cell starts with """ # BEGIN TEST CONFIG
                if source.strip().startswith('""" # BEGIN TEST CONFIG'):

                    logging_variables = FastAPINotebookBuilder.extract_log_variables(
                        cell
                    )

                    # Extract all assert statements using regex (multiline enabled)
                    matches = re.findall(r"assert\s+(.+?)(?:,|$)", source, re.DOTALL)

                    # Clean and join multiline conditions
                    cleaned_matches = [
                        " ".join(condition.split()) for condition in matches
                    ]

                    # Extract the first line containing `points:`
                    points_line = next(
                        (line for line in source.split("\n") if "points:" in line), None
                    )
                    points_value = None
                    if points_line:
                        try:
                            points_value = float(points_line.split(":")[-1].strip())
                        except ValueError:
                            points_value = None  # Handle cases where the points value is not a valid number

                    # Add assertions and points to the dictionary
                    results_dict[cell_index] = {
                        "assertions": cleaned_matches,
                        "question": question_name,
                        "points": points_value,
                        "logging_variables": logging_variables,
                    }

                    results_dict = FastAPINotebookBuilder.tag_questions(results_dict)

        return results_dict
