"""
Scoring and logging script.

Scores and logs the results of a single task or all tasks at once.
"""

import glob
import os
import importlib
from collections.abc import Callable
from typing import Tuple, Optional

import numpy as np
import pandas as pd

from visualize_task import TaskVisualizer
from util_helpers import load_task_data, parse_logging_args
from config import (LOGS_DIR, SOLUTION_DIR, SOLUTION_DIR_NAME,
                         VISUALIZE_SINGLE_TASK_EXAMPLES,
                         SOLUTION_FUNCTION_NAME,
                         SCORE_COLOR_THRESHOLD_1, SCORE_COLOR_THRESHOLD_2, SCORE_COLOR_THRESHOLD_3)

class TaskScorer:
    """
    Scores solutions for tasks and generates logs.

    Tasks can either be scored individually or all together.

    When a task is scored individually, a log is generated which lists all the correct examples,
    incorrect examples, and the examples that crashed. If --verbose is set (via command line arguments)
    then the specific error that caused each crash is also listed. Also, if VISUALIZE_SINGLE_TASK_EXAMPLES 
    is True (in the config), then a matplotlib figure will be created that visualizes the task.

    When the tasks are scored all together (specified by the --all_tasks flag in the terminal), a text 
    log and an excel log are created in the LOGS_DIR (logging directory specified in the config).
        - Text Log: 
            - Each correctly solved task is listed along with its score. 
            - Each incorrectly solved task lists all the correct examples and all the incorrect examples.
            - Each crashed task lists all the correct, incorrect, and crashed examples separately.
                - (if --verbose) the specific error that caused each crash is also listed.

        - Excel Log:
            - Lists each task with it's score and percent of examples that are correct.
    
    A task is only considered correct if every example is correct; an example is correct if the expected 
    and obtained outputs are the same. Correct tasks receive a score of 
    max(1, 2500-(number of characters in the solution)), while incorrect solutions receive a score of 0.001.
    
    Attributes:
        NUM_TASKS (int): Total number of tasks.
        MAX_TASK_SCORE (int): Maximum available score for a task.
        MAX_OVERALL_SCORE (int): The maximum score available for all tasks combined; i.e. NUM_TASKS*MAX_TASK_SCORE.

        task_num (str): The task number; set to 0 if `--all_tasks` is set.
        verbose_errors_flag (bool): Whether to display the errors for each example (if set to true) or to simply list out every example that crashed.
    """

    NUM_TASKS = 400
    MAX_TASK_SCORE = 2500
    MAX_OVERALL_SCORE = 1000000

    def __init__(self, task_num: str, verbose_errors_flag: bool):
        """
        Initializes an instance with the task to be process and the verbosity of the logs.

        Args:
            task_num (str): Task number; e.g. 1 for task001.
            verbose_errors_flag (bool): Specifies log error verbosity.
        """

        self.task_num = task_num
        self.verbose_errors_flag = verbose_errors_flag
    
    #=====Main Logging Functions=====
            
    def _score_log_all_tasks(self):
        """
        Scores all tasks and creates logs for the results.
        """

        unattempted_tasks = [f"task{str(i).zfill(3)}" for i in range(1, self.NUM_TASKS+1)]
        attempted_tasks = sorted([task_path[-10:-3] for task_path in glob.glob(os.path.join(SOLUTION_DIR, "task*.py"))])
        correct_tasks = []
        incorrect_tasks = []
        crashed_tasks = []

        logging_df_columns = ["Score", "Percent Correct", "Correct Examples", "Incorrect Examples", "Crashed Examples", "Crashed Example Errors"]
        logging_df = pd.DataFrame(index=unattempted_tasks, columns=logging_df_columns)

        for task_name in attempted_tasks:
            unattempted_tasks.remove(task_name)

            task_results_dict, _ = self._process_task_solution(task_name)
            logging_df.loc[task_name] = task_results_dict

            if task_results_dict["Score"]>0.001:
                correct_tasks.append(task_name)
            elif len(task_results_dict["Crashed Examples"])==0:
                incorrect_tasks.append(task_name)
            else:
                crashed_tasks.append(task_name) 
        
        for task_name in unattempted_tasks:
            logging_df.loc[task_name] = {
                "Score": 0.001,
                "Percent Correct": 0,
                "Correct Examples": [],
                "Incorrect Examples": [],
                "Crashed Examples": [],
                "Crashed Example Errors": []
            }
        
        self._create_log(logging_df, correct_tasks, incorrect_tasks, crashed_tasks, unattempted_tasks)
        self._create_excel(logging_df, logging_df_columns)
    
    def _score_log_single_task(self, task_name: str):
        """
        Scores a single task and optionally visualizes it.

        Args:
            task_name (str): Task identifier; e.g. `"task001"`.
        """

        task_results_dict, solution_results = self._process_task_solution(task_name, True)

        if (len(task_results_dict["Crashed Example Errors"])>0) and (task_results_dict["Crashed Example Errors"][0] == "--function_not_found"):
            print(f"NameError: Function \"{SOLUTION_FUNCTION_NAME}\" not found; the solution cannot be tested.")
            return

        self._create_single_log(task_name, task_results_dict)

        print(f"====================VISUALIZATION====================")
        if VISUALIZE_SINGLE_TASK_EXAMPLES:
            print("You have set VISUALIZE_SINGLE_TASK_EXAMPLES in the config file to True.")
            print("Creating plot...")
            TV_i = TaskVisualizer(task_name, solution_results)
            TV_i.show()
            print("Plot closed.")
        
        else:
            print("You have set VISUALIZE_SINGLE_TASK_EXAMPLES in the config file to False; as such a plot will not be created.")
            print("If you would like to visualize the examples of this task, please set VISUALIZE_SINGLE_TASK_EXAMPLES to True in the config file.")
    
    #=====Helper Functions=====
    
    def _process_task_solution(self, task_name: str, store_results: bool=False) -> Tuple[dict, list]:
        """
        Runs a task's solution and returns the results

        Args:
            task_name (str): Task identifier.
            store_results (bool): If True, store solution outputs for visualization.

        Returns:
            Tuple[dict, list]: A dictionary with scoring details and a list of solution outputs.
        """

        task_data = load_task_data(task_name)
        tentative_score, solution_function = self._load_solution_function(task_name)
        task_results_dict, solution_results = self._test_task_solution(task_data, solution_function, tentative_score, store_results)
        return task_results_dict, solution_results
    
    def _load_solution_function(self, task_name: str) -> Tuple[int, Optional[Callable]]:
        """
        Loads the solution function from the appropriate Python file and computes the score the solution
        would receive if it's correct.

        Args:
            task_name (str): Task identifier.

        Returns:
            Tuple[int, Callable]: Tentative score and the main solution function.
        """

        task_module = importlib.import_module(f"{SOLUTION_DIR_NAME}.{task_name}")
        solution_size = os.path.getsize(os.path.join(SOLUTION_DIR,f"{task_name}.py"))
        tentative_score = max(1, 2500-solution_size)
        main_solution_function = getattr(task_module, SOLUTION_FUNCTION_NAME)

        if not callable(main_solution_function):
            print(f"Error; the function {SOLUTION_FUNCTION_NAME} is not a function.")

        return tentative_score, main_solution_function
    
    def _test_task_solution(self, task_data: list, solution_function: Callable, tentative_score: int, store_results: bool) -> Tuple[dict, list]:
        """
        Tests a solution function against task examples and records results.

        Args:
            task_data (list): List of examples.
            solution_function (Callable): Solution function.
            tentative_score (int): Score if all examples are correct.
            store_results (bool): If True, store solution outputs for visualization.

        Returns:
            Tuple[dict, list]: Dictionary with score details and list of solution outputs.
        """

        if solution_function is None:
            tested_solution_dict = {
                "Score": 0.001,
                "Percent Correct": 0,
                "Correct Examples": [],
                "Incorrect Examples": [],
                "Crashed Examples": [1], #forces current task to be listed as a crashed task while maintaining dictionary type conistency.
                "Crashed Example Errors": ["--function_not_found"] #flag that allows _create_log to log this error properly.
            }

            #dummy arrays for visualization
            results = [(np.array(example_i["output"])*0).tolist() for example_i in task_data]

            return tested_solution_dict, results


        correct_list = []
        incorrect_list = []
        crashed_list = []
        error_list = []

        results = []

        for i ,example_i in enumerate(task_data):
            example_input = example_i["input"]
            example_expected_output = example_i["output"]

            try:
                result = solution_function(example_input)

                if np.array_equal(result, example_expected_output):
                    correct_list.append(i)
                else:
                    incorrect_list.append(i)

            except Exception as e:
                crashed_list.append(i)
                error_list.append(repr(e))

                #dummy array for visualization
                result = (np.array(example_expected_output)*0).tolist()
            
            finally:
                results.append(result)

        
        if len(correct_list) != len(task_data):
            tentative_score = 0.001
        
        tested_solution_dict = {
            "Score": tentative_score,
            "Percent Correct": round(len(correct_list)/len(task_data)*100, 2),
            "Correct Examples": correct_list,
            "Incorrect Examples": incorrect_list,
            "Crashed Examples": crashed_list,
            "Crashed Example Errors": error_list
        }

        if not store_results:
            results=[]

        return tested_solution_dict, results
    
    def _create_log(self, logging_df: pd.DataFrame, correct_tasks: list, incorrect_tasks: list, crashed_tasks: list, unattempted_tasks: list):
        """
        Creates a log that specifies which tasks were correct, incorrect, and which ones crashed.

        Args:
            logging_df (pd.DataFrame): DataFrame containing task results.
            correct_tasks (list): List of correctly solved tasks.
            incorrect_tasks (list): List of incorrectly solved tasks.
            crashed_tasks (list): List of tasks that crashed.
            unattempted_tasks (list): List of tasks that were not attempted.
        """

        with open(os.path.join(LOGS_DIR, "results_log.txt"), "w") as results_log:
            results_log.write(f"====================RESULTS SUMMARY====================\n")
            results_log.write(f"Score: {round(logging_df['Score'].sum(),3)}/{self.MAX_OVERALL_SCORE}\n")
            results_log.write(f"Correctly solved: {len(correct_tasks)}/{self.NUM_TASKS}\n")
            results_log.write(f"Incorrectly Solved: {len(incorrect_tasks)}/{self.NUM_TASKS}\n")
            results_log.write(f"Program Crashed: {len(crashed_tasks)}/{self.NUM_TASKS}\n")
            results_log.write(f"Unattempted Tasks: {len(unattempted_tasks)}/{self.NUM_TASKS}\n")
            results_log.write("\n")

            results_log.write(f"====================CORRECTLY SOLVED TASKS====================\n")
            for task in correct_tasks:
                results_log.write(f"{task}: {logging_df.loc[task]['Score']}/{self.MAX_TASK_SCORE}\n\n")
            
            results_log.write(f"====================INCORRECTLY SOLVED TASKS====================\n")
            for task in incorrect_tasks:
                results_log.write(f"{task}:\n")
                results_log.write(f"\tCorrect Examples: {logging_df.loc[task]['Correct Examples']}\n")
                results_log.write(f"\tIncorrect Examples: {logging_df.loc[task]['Incorrect Examples']}\n\n")
            
            results_log.write(f"====================CRASHED TASKS====================\n")
            for task in crashed_tasks:
                if logging_df.loc[task]["Crashed Example Errors"][0] == "--function_not_found":
                    results_log.write(f"{task}: NameError-Function \"{SOLUTION_FUNCTION_NAME}\" not found.\n\n")
                else:
                    results_log.write(f"{task}:\n")
                    results_log.write(f"\tCorrect Examples: {logging_df.loc[task]['Correct Examples']}\n")
                    results_log.write(f"\tIncorrect Examples: {logging_df.loc[task]['Incorrect Examples']}\n")
                    
                    if self.verbose_errors_flag:
                        results_log.write(f"\tCrashed Examples:\n")

                        crashed_tasks_i = logging_df.loc[task]["Crashed Examples"]
                        errors_i = logging_df.loc[task]["Crashed Example Errors"]
                        for j, example_j in enumerate(crashed_tasks_i):
                            results_log.write(f"\t\t{example_j}: {errors_i[j]}\n")
                    else:
                        results_log.write(f"\tCrashed Examples: {logging_df.loc[task]['Crashed Examples']}\n")
                    
                    results_log.write(f"\n")
            
            results_log.write(f"====================UNATTEMPTED TASKS====================\n")
            for task_i in unattempted_tasks:
                results_log.write(f"{task_i}\n")
        
        print(f"Created results log at {os.path.join(LOGS_DIR, 'results_log.txt')}")

    def _create_excel(self, logging_df: pd.DataFrame, logging_df_columns: list):
        """
        Generates an Excel sheet summarizing scores and percent correct for all tasks.

        Args:
            logging_df (pd.DataFrame): DataFrame containing task results.
            logging_df_columns (list): Column names of logging_df.
        """

        logging_df[logging_df_columns[:2]].style.apply(self._style_percent_correct, subset=["Percent Correct"]).apply(self._style_score, subset=["Score"]).to_excel(os.path.join(LOGS_DIR, "results.xlsx"))
        print(f"Created results excel sheet at {os.path.join(LOGS_DIR, 'results.xlsx')}")

    def _style_percent_correct(self, percent_correct: pd.Series) -> np.ndarray:
        """
        Calculates styling of the "Percent Correct" column of each task.

        Args:
            percent_correct (pd.Series): The "Percent Correct" column of the results/logging dataframe.

        Returns:
            np.ndarray: CSS style strings for styling Excel output.
        """

        score_conditions = [percent_correct<25, percent_correct<50, percent_correct<75, percent_correct<=100]
        score_colors = ["background-color: #ff081b", "background-color: #fe8015", "background-color: #fdf709", "background-color: #87e155"]
        return np.select(score_conditions, score_colors, default="#000000")

    def _style_score(self, score: pd.Series) -> np.ndarray:
        """
        Calculates styling of the "Score" column of each task.

        Args:
            percent_correct (pd.Series): The "Score" column of the results/logging dataframe.

        Returns:
            np.ndarray: CSS style strings for styling Excel output.
        """
        score_conditions = [score<SCORE_COLOR_THRESHOLD_1, score<SCORE_COLOR_THRESHOLD_2, score<SCORE_COLOR_THRESHOLD_3, score<=2500]
        score_colors = ["background-color: #ff081b", "background-color: #fe8015", "background-color: #fdf709", "background-color: #87e155"]
        return np.select(score_conditions, score_colors, default="#000000")
    
    def _create_single_log(self, task_name: str, task_results_dict: dict):
        """
        Prints results for a single task.

        Args:
            task_name (str): Task identifier.
            task_results_dict (dict): Dictionary containing the score and example results.
        """

        num_total_examples = len(task_results_dict["Correct Examples"]) + len(task_results_dict["Incorrect Examples"]) + len(task_results_dict["Crashed Examples"])
        print(f"===================={task_name.upper()} RESULTS SUMMARY====================")
        print(f"Score: {task_results_dict['Score']}/{self.MAX_TASK_SCORE}\n")
        print(f"Percent Correct: {task_results_dict['Percent Correct']}\n")
        print(f"Correctly solved: {len(task_results_dict['Correct Examples'])}/{num_total_examples}")
        print(f"\t- {task_results_dict['Correct Examples']}\n")
        print(f"Inorrectly solved: {len(task_results_dict['Incorrect Examples'])}/{num_total_examples}")
        print(f"\t- {task_results_dict['Incorrect Examples']}\n")
        print(f"Crashed: {len(task_results_dict['Crashed Examples'])}/{num_total_examples}")
        if self.verbose_errors_flag:
            for i, example_i in enumerate(task_results_dict['Crashed Examples']):
                print(f"\t- {example_i}: {task_results_dict['Crashed Example Errors'][i]}")
        else:
            print(f"\t- {task_results_dict['Crashed Examples']}\n")

    
    #=====Entry Point=====
    
    def score(self):
        """
        Based on the value of `task_num`, scores all the tasks (if it's 0) or a single task.
        """

        #task_num is set to 0 if the --all_task flag is set in the CLI
        if self.task_num == "0":
            self._score_log_all_tasks()
        else:
            self._score_log_single_task(f"task{self.task_num.zfill(3)}")

if __name__ == "__main__":
    task_num, verbose_errors_flag = parse_logging_args()

    TS_i = TaskScorer(task_num, verbose_errors_flag)

    TS_i.score()