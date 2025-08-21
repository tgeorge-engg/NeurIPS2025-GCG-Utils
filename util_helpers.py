"""
Utility functions for parsing CLI arguments and loading task data.
"""

import os
import json
import argparse
from typing import Tuple

from config import DATA_DIR

def parse_visualization_args() -> str:
    """
    Parses command line arguments for visualize_task.py.

    Returns:
        str: Task number.
    """

    parser = argparse.ArgumentParser(description="Visualize tasks with interactive plots.")
    parser.add_argument("task_num", type=_validate_task_num, help="Task number (e.g. 1 for task001)")

    return parser.parse_args().task_num

def parse_logging_args() -> Tuple[str, bool]:
    """
    Parses command line arguments for score_task.py.

    Returns:
        Tuple[str, bool]: Task number and verbosity flag.
    """

    parser = argparse.ArgumentParser(description="Visualize tasks with interactive plots.")
    parser.add_argument("task_num", type=_validate_task_num, help="Task number from 1 to 400 (e.g. 1 for task001)", nargs="?")
    parser.add_argument("-a", "--all_tasks", action="store_true", help="If this flag is set, all tasks will be scored and result logs will be created.")
    parser.add_argument("-v", "--verbose", action="store_true", help="If this flag is set, the logs won't display the error caused by each example that crashed.")

    args = parser.parse_args()

    # If the --all_tasks flag is set, then task_num is set to 0 which signals the TaskScorer to score all the tasks.
    # If arg.task_num is not given and --all_tasks is not set, task_num is set to 0.
    task_num = "0" if (args.all_tasks or (args.task_num is None)) else args.task_num

    return task_num, args.verbose

def _validate_task_num(task_num: str) -> str:
    """
    Sanitizes the `task_num` input.

    Returns:
        str: Task number.
    """

    if (not task_num.isdigit()) or (int(task_num)>400) or (int(task_num)<1):
        raise argparse.ArgumentTypeError(f"\"{task_num}\" is not a valid task number; you must input an integer from 1 to 400")
    
    # Converted back to string to avoid conflicts and to strip extra zeroes; the necessary amount of zerous is already
    # added later.
    return str(int(task_num))

def load_task_data(task_name: str) -> list:
    """
    Loads and merges all the examples/data of a specified task.

    Each task is expected to be a JSON object with keys "train", "test, and "arc-gen".

    Returns:
        list: Combined list of all examples in the specified task.
    """

    with open (os.path.join(DATA_DIR, f"{task_name}.json"), "r") as task_file:
        task_json = json.load(task_file)
    return task_json["train"] + task_json["test"] + task_json["arc-gen"]
