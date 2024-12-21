from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class FastAPINotebookBuilder:
    path: str

    def __post_init__(self):
        self.root_path, self.filename = FastAPINotebookBuilder.get_filename_and_root(
            self.path
        )

        self.import_cell = self.extract_first_cell()
        self.import_cell = self.add_imports()

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
        lines.append(f'initialize_assignment("{self.filename}")')
        lines = [line.replace("\n", "") for line in lines]

        return "\n".join(lines)

    def extract_first_cell(self):
        with open(self.path, "r", encoding="utf-8") as f:
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
