# NeurIPS2025-GCG-Utils
Task visualization and scoring scripts for the NeurIPS 2025 - Google Code Golf Championship.

## Main Features
- Visualization: View every input-output pair in a task with an interactive matplotlib figure that allows you to fluidly navigate between pairs.

- Scoring & Logging: Score the attempted tasks and create a log summarizing the results.

## Installation
```bash
git clone https://github.com/tgeorge-engg/NeurIPS2025-GCG-Utils.git
cd NeurIPS2025-GCG-Utils
pip install -r requirements.txt
```
**Note:** The contents of this repository are meant to be placed inside your main project directory. It is recommended that you rename the cloned folder and make that you main project directory, or move the contents into your main project directory.

## Recommended Directory Structure
```bash
.
├── config.py
├── util_helpers.py
├── visualize_task.py
├── score_tasks.py
├── data/
├── task_solutions/
├── logs/
├── requirements.txt
└── testing
    ├── test_data/
    ├── test_task_solutions/
    └── test_descriptions.txt
```

| Directory/File                | Description |
|-------------------------------|-------------|
| `config.py`                     | Holds all global configuration for the main utility scripts. |
| `util_helpers.py`               | Contains helper functions for the utility scripts. |
| `visualize_task.py`             | One of the main scripts; used for visualizing tasks. |
| `score_tasks.py`                | One of the main scripts; used to score and log tasks. |
| `data`<sup>*</sup>              | Directory containing all the task json files. |
| `task_solutions`<sup>*</sup>    | Directory containing all the task solution files. |
| `logs`<sup>*</sup>              | Directory containing the generated logs. |
| `requirements.txt`              | List of libraries required for the scripts to work. |
| `testing/test_data`             | Directory containing the task json files used for testing. |
| `testing/test_task_solutions`   | Directory containing the task solution files used for testing. |
| `testing/test_descriptions.txt` | File containing descriptions of the provided test tasks and solutions. |
<sup>*</sup> Not included in this repository.

## Config
The main scripts (visualize_task.py and score_tasks.py) rely on global configurations that are stored in `config.py`.
You can modify these settings based on your directory structure and preferences.

| Setting                        | Description |
|--------------------------------|-------------|
| `DATA_DIR`                       | Path to the directory where the tasks json files are stored. |
| `SOLUTION_DIR`                   | Path to the directory where the task solution files are stored. |
| `SOLUTION_DIR_NAME`              | Module-like name of the directory where the solution files are stored; e.g. if the files are stored in "./testing/task_sols", the name would be "testing.task_sols".|
| `LOGS_DIR`                       | Path to the directory where the logs should be stored. |
| `VISUALIZE_SINGLE_TASK_EXAMPLES` | Flag that specifies if a matplotlib figure should be created when scoring a single task. |
| `COLOR_DICT`                     | Dictionary mapping each integer from 0 to 9 to a color represented with a hexadecimal code. |
| `PLOT_TEXT_SETTINGS`             | Dictionary containing settings for the text in the matplotlib figures. |
| `SOLUTION_FUNCTION_NAME`         | What the task solution functions are called. |
| `SCORE_COLOR_THRESHOLD_[1,2,3]`  | Thresholds used to color the excel log's cells. |

## Usage
### Visualization
```bash
python3 visualize_task.py [-h] <task_num>
```

| Argument                | Description |
|-------------------------|-------------|
| `-h`, `--help`          | Flag to show the help message. |
| `task_num` (positional) | Specific task number to visualize. |

Example:
```bash
#visualize task 39
python3 visualize_task.py 39
```
### Scoring & Logging
```bash
python3 score_tasks.py [-h] [-a] [-v] [task_num]
```
| Argument              | Description |
|-----------------------|-------------|
| `-h`, `--help`        | Flag to show the help message. |
| `-a`, `--all_tasks`   | Flag to score all tasks. |
| `-v`, `--verbose`     | Flag to display the error message for every input-output pair of a crashed task. |
| `task_num` (optional) | Specific task number to score. If --all_tasks is set and a task number is given, all the tasks will be scored. If --all_tasks isn't set and no task number is given, all tasks will be scored.|

Examples:
```bash
#score task 39
python3 score_tasks.py 39

#score all tasks with verbose error logging
python3 score_tasks.py --all_tasks --verbose
```

## Testing
In the testing folder you will find toy test tasks [testing/test_data](testing/test_data) and solutions to said tasks [testing/test_task_solutions](testing/test_task_solutions). In order to show the behaviour of the scripts in various situations, not all of the solutions solve the task correctly. A more complete description of the tests and the expected outputs can be found in [testing/test_descriptions.txt](testing/test_descriptions.txt).

In order to test the scripts with the provided test tasks, you must first set the following in [config.py](config.py):

```python
DATA_DIR = "./testing/test_data"
SOLUTION_DIR = "./testing/test_task_solutions"
SOLUTION_DIR_NAME = "testing.test_task_solutions"
```

You can then run the main scripts as usual; please read the test descriptions file before running any tests.
