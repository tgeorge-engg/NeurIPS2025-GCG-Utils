"""
Config file for paths, plot settings, etc.
"""

DATA_DIR = "./data"
SOLUTION_DIR = "./task_solutions"
SOLUTION_DIR_NAME = "task_solutions" #used by importlib to load solution functions.
LOGS_DIR = "./logs"

VISUALIZE_SINGLE_TASK_EXAMPLES = True
COLOR_DICT = {
    0: "#000000", #black
    1: "#1e93ff", #blue
    2: "#fa3e31", #red
    3: "#4fcc30", #green
    4: "#ffdd00", #yellow
    5: "#999999", #grey
    6: "#e53ba3", #pink
    7: "#ff861c", #orange
    8: "#88d8f1", #light blue
    9: "#931131", #maroon
}
PLOT_TEXT_SETTINGS = {
    "ha": "center",
    "va": "center",
    "size": "small",
    "bbox":{
        "boxstyle": "square",
        "facecolor": "#ffffff",
        "alpha": 0.75
    }
}

#the function name the scripts should look for when loading the solution function
SOLUTION_FUNCTION_NAME = "p"

#scoring thresholds used to color excel logs
SCORE_COLOR_THRESHOLD_1 = 625
SCORE_COLOR_THRESHOLD_2 = 1250
SCORE_COLOR_THRESHOLD_3 = 1875