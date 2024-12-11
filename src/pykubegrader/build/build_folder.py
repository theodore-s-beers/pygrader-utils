from dataclasses import dataclass, field
import os
import shutil
import nbformat
import subprocess
import sys
import argparse
import logging

@dataclass
class NotebookProcessor:
    root_folder: str
    solutions_folder: str = field(init=False)
    verbose: bool = False
    log: bool = True

    def __post_init__(self):
        # Define the folder to store solutions
        self.solutions_folder = os.path.join(self.root_folder, "_solutions")
        os.makedirs(self.solutions_folder, exist_ok=True)
        
        # Configure logging
        log_file_path = os.path.join(self.solutions_folder, "notebook_processor.log")
        logging.basicConfig(
            filename=log_file_path,  # Name of the log file
            level=logging.INFO,  # Logging level
            format="%(asctime)s - %(levelname)s - %(message)s"  # Log format
        )

        self.logger = logging.getLogger(__name__)  # Get a logger instance

    def process_notebooks(self):
        """
        Recursively processes Jupyter notebooks in a given folder and its subfolders.

        The function performs the following steps:
        1. Iterates through all files within the root folder and subfolders.
        2. Identifies Jupyter notebooks by checking file extensions (.ipynb).
        3. Checks if each notebook contains assignment configuration metadata.
        4. Processes notebooks that meet the criteria using `otter assign` or other defined steps.

        Prerequisites:
            - The `has_assignment` method should be implemented to check if a notebook
            contains the required configuration for assignment processing.
            - The `_process_single_notebook` method should handle the specific processing
            of a single notebook, including moving it to a new folder or running
            additional tools like `otter assign`.

        Raises:
            - OSError: If an issue occurs while accessing files or directories.

        Example:
            class NotebookProcessor:
                def __init__(self, root_folder):
                    self.root_folder = root_folder

                def has_assignment(self, notebook_path):
                    # Implementation to check for assignment configuration
                    return True  # Replace with actual check logic

                def _process_single_notebook(self, notebook_path):
                    # Implementation to process a single notebook
                    print(f"Processing notebook: {notebook_path}")

            processor = NotebookProcessor("/path/to/root/folder")
            processor.process_notebooks()
        """
        ipynb_files = []
        
        # Walk through the root folder and its subfolders
        for dirpath, _, filenames in os.walk(self.root_folder):
            for filename in filenames:
                # Check if the file is a Jupyter notebook
                if filename.endswith(".ipynb"):
                    notebook_path = os.path.join(dirpath, filename)
                    ipynb_files.append(notebook_path)
        
        for notebook_path in ipynb_files:
            # Check if the notebook has the required assignment configuration
            if self.has_assignment(notebook_path):
                
                print(f"notebook_path = {notebook_path}")
                
                # Process the notebook if it meets the criteria
                self._process_single_notebook(notebook_path)
                        
    def _print_and_log(self, message):
        """
        Print a message and log it to the logger.
        """
        if self.verbose:
            print(message)
        
        if self.log:    
            self.logger.info(message)


    def _process_single_notebook(self, notebook_path):
        notebook_name = os.path.splitext(os.path.basename(notebook_path))[0]
        notebook_subfolder = os.path.join(self.solutions_folder, notebook_name)
        os.makedirs(notebook_subfolder, exist_ok=True)

        new_notebook_path = os.path.join(notebook_subfolder, os.path.basename(notebook_path))
        if os.path.abspath(notebook_path) != os.path.abspath(new_notebook_path):
            shutil.move(notebook_path, new_notebook_path)
            self._print_and_log(f"Moved: {notebook_path} -> {new_notebook_path}")
        else:
            self._print_and_log(f"Notebook already in destination: {new_notebook_path}")

        self.run_otter_assign(new_notebook_path, os.path.join(notebook_subfolder, "dist"))

        student_notebook = os.path.join(notebook_subfolder, "dist", "student", f"{notebook_name}.ipynb")
        self.clean_notebook(student_notebook)
        shutil.copy(student_notebook, self.root_folder)
        print(f"Copied and cleaned student notebook: {student_notebook} -> {self.root_folder}")

    @staticmethod
    def has_assignment(notebook_path, *tags):
        """
        Determines if a Jupyter notebook contains any of the specified configuration tags.

        This method checks for the presence of specific content in a Jupyter notebook
        to identify whether it includes any of the required headings or tags.

        Args:
            notebook_path (str): The file path to the Jupyter notebook to be checked.
            *tags (str): Variable-length argument list of tags to search for.
                        Defaults to ("# ASSIGNMENT CONFIG",).

        Returns:
            bool: True if the notebook contains any of the specified tags, False otherwise.

        Dependencies:
            - The `check_for_heading` function must be implemented. It should search
            for specific headings or content in a notebook file and return a boolean
            value indicating if any of the tags exist.

        Example:
            def check_for_heading(notebook_path, keywords):
                # Mock implementation of content check
                with open(notebook_path, 'r') as file:
                    content = file.read()
                return any(keyword in content for keyword in keywords)

            notebook_path = "path/to/notebook.ipynb"
            # Check for default tags
            contains_config = has_assignment(notebook_path)
            print(f"Contains assignment config: {contains_config}")

            # Check for custom tags
            contains_custom = has_assignment(notebook_path, "# CUSTOM CONFIG", "# ANOTHER CONFIG")
            print(f"Contains custom config: {contains_custom}")
        """
        # Default tags if none are provided
        if not tags:
            tags = ["# ASSIGNMENT CONFIG"]

        # Use the helper function to check for the presence of any specified tag
        return check_for_heading(notebook_path, tags)

    @staticmethod
    def run_otter_assign(notebook_path, dist_folder):
        """
        Runs `otter assign` on the given notebook and outputs to the specified distribution folder.
        """
        try:
            os.makedirs(dist_folder, exist_ok=True)
            command = ["otter", "assign", notebook_path, dist_folder]
            subprocess.run(command, check=True)
            print(f"Otter assign completed: {notebook_path} -> {dist_folder}")
        except subprocess.CalledProcessError as e:
            print(f"Error running `otter assign` for {notebook_path}: {e}")
        except Exception as e:
            print(f"Unexpected error during `otter assign` for {notebook_path}: {e}")

    @staticmethod
    def clean_notebook(notebook_path):
        """
        Cleans a Jupyter notebook to remove unwanted cells and set cell metadata.
        """
        clean_notebook(notebook_path)


def check_for_heading(notebook_path, search_strings):
    """
    Checks if a Jupyter notebook contains a heading cell whose source matches any of the given strings.
    """
    try:
        with open(notebook_path, "r", encoding="utf-8") as f:
            notebook = nbformat.read(f, as_version=4)
            for cell in notebook.cells:
                if cell.cell_type == "raw" and cell.source.startswith("#"):
                    if any(search_string in cell.source for search_string in search_strings):
                        return True
    except Exception as e:
        print(f"Error reading notebook {notebook_path}: {e}")
    return False


def clean_notebook(notebook_path):
    """
    Removes specific cells and makes Markdown cells non-editable and non-deletable by updating their metadata.
    """
    try:
        with open(notebook_path, "r", encoding="utf-8") as f:
            notebook = nbformat.read(f, as_version=4)

        cleaned_cells = []
        for cell in notebook.cells:
            if not hasattr(cell, "cell_type") or not hasattr(cell, "source"):
                continue

            if (
                "## Submission" not in cell.source
                and "# Save your notebook first," not in cell.source
            ):
                if cell.cell_type == "markdown":
                    cell.metadata["editable"] = cell.metadata.get("editable", False)
                    cell.metadata["deletable"] = cell.metadata.get("deletable", False)
                if cell.cell_type == "code":
                    cell.metadata["tags"] = cell.metadata.get("tags", [])
                    if "skip-execution" not in cell.metadata["tags"]:
                        cell.metadata["tags"].append("skip-execution")

                cleaned_cells.append(cell)
            else:
                print(f"Removed cell: {cell.source.strip()[:50]}...")

        notebook.cells = cleaned_cells

        with open(notebook_path, "w", encoding="utf-8") as f:
            nbformat.write(notebook, f)
        print(f"Cleaned notebook: {notebook_path}")

    except Exception as e:
        print(f"Error cleaning notebook {notebook_path}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Recursively process Jupyter notebooks with '# ASSIGNMENT CONFIG', move them to a solutions folder, and run otter assign."
    )
    parser.add_argument("root_folder", type=str, help="Path to the root folder to process")
    args = parser.parse_args()

    processor = NotebookProcessor(args.root_folder)
    processor.process_notebooks()


if __name__ == "__main__":
    sys.exit(main())
