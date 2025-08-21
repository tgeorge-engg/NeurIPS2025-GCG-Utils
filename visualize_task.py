"""
Task visualization script.

Creates an interactive matplotlib GUI with controls to inspect input/output matrices (and optional solution results).
"""

from typing import Optional

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, TextBox
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.patches as mpatches

from util_helpers import load_task_data, parse_visualization_args
from config import (COLOR_DICT, PLOT_TEXT_SETTINGS)

class TaskVisualizer:
    """
    Creates an interactive matplotlib figure to visualize a specified task.

    Attributes:
        CMAP (matplotlib.colors.ListedColormap): Mapping that specifies which number maps to which color.
        CMAP_NORM (matplotlib.colors.BoundaryNorm): Helper object to enforce CMAP's color mapping.
        LEGEND_HANDLES (list): List of colored patches used to show the color mapping in the legend.
        LEGEND_LABELS (list): Strings of the possible numbers to use in the legend.

        task_name (str): Task identifier; e.g. `"task001"`.
        solution_results (list or None): List of solution outputs.
    """

    CMAP = ListedColormap([COLOR_DICT[i] for i in range(10)])
    CMAP_NORM = BoundaryNorm(np.arange(-0.5, 10.5, 1), CMAP.N)
    LEGEND_HANDLES = [mpatches.Patch(color=COLOR_DICT[i]) for i in range(10)]
    LEGEND_LABELS = [str(i) for i in range(10)]

    def __init__(self, task_name: str, solution_results: Optional[list]=None):
        """
        Initializes an instance with the task identifier and list of solution outputs.

        Args:
            task_name (str): Task identifier.
            solution_results (list or None): List of solution outputs.
        """

        self.task_data = load_task_data(task_name)
        self.solution_results = [] if solution_results is None else solution_results

        self.current_example_ind = 0
        self.show_numbers = False

        num_subplots = 2 + int((len(self.solution_results)>0))
        self.fig, self.axes = plt.subplots(1, num_subplots)
        plt.subplots_adjust(bottom=0.3)
        self.fig.suptitle(f"Example {self.current_example_ind} / {len(self.task_data) - 1}")
        self.fig.legend(handles=self.LEGEND_HANDLES, labels=self.LEGEND_LABELS, loc="upper right")

        self._init_widgets()

        self._plot_example()
    
    #=====Plot Creation=====
    
    def _init_widgets(self):
        """
        Creates interactive controls for the figure.
        """

        #slider used to navigate between examples.
        ax_slider = plt.axes([0.1, 0.18, 0.8, 0.03])
        self.slider = Slider(ax_slider, "Example", 0, len(self.task_data) - 1, valinit=0, valstep=1)
        self.slider.on_changed(self._update_example)
        
        #toggle used to show/hide number overlay on plotted matrix.
        ax_toggle = plt.axes([0.1, 0.05, 0.2, 0.1])
        self.number_toggle_button = Button(ax_toggle, "Toggle Numbers")
        self.number_toggle_button.on_clicked(self._toggle_numbers)

        #text input to jump to specific example.
        ax_text = plt.axes([0.465, 0.05, 0.07, 0.1])
        self.text_box = TextBox(ax_text, "", "0", textalignment="center")
        self.text_box.on_submit(self._text_submitted)

        ax_prev = plt.axes([0.68, 0.05, 0.1, 0.1])
        self.prev_button = Button(ax_prev, "Prev")
        self.prev_button.on_clicked(self._prev_example)

        ax_next = plt.axes([0.8, 0.05, 0.1, 0.1])
        self.next_button = Button(ax_next, "Next")
        self.next_button.on_clicked(self._next_example)
    
    def _plot_example(self):
        """
        Plot the current example's input, output, and (optionally) solution.
        """

        self._plot_matrix(self.axes[0], self.task_data[self.current_example_ind]["input"], "Input")
        self._plot_matrix(self.axes[1], self.task_data[self.current_example_ind]["output"], "Output")

        if self.solution_results:
            self._plot_matrix(self.axes[2], self.solution_results[self.current_example_ind], "Result")
        
        self.fig.canvas.draw_idle()

    def _plot_matrix(self, axis: plt.Axes, matrix: list, title: str):
        """
        Plot a specified matrix.

        Attributes:
            axis (plt.Axes): Axis (subplot) to draw the matrix on.
            matrix (list): Matrix to draw.
            title (str): Title of the subplot.
        """

        axis.cla()
        matrix = np.array(matrix, dtype=np.uint8)
        axis.matshow(matrix, cmap=self.CMAP, norm=self.CMAP_NORM)

        #overlay numbers inside each cell if True.
        if self.show_numbers:
            for (i, j), val in np.ndenumerate(matrix):
                axis.text(j, i, val, **PLOT_TEXT_SETTINGS)

        axis.set_title(title)
        axis.set_xlabel(f"{matrix.shape}")
        axis.set_xticks([])
        axis.set_yticks([])
    
    #=====Event Handlers=====

    def _update_example(self, val: str):
        """
        Event handler that handles requests to change the currently show example.

        Args:
            val (str): Index of the example to be shown.
        """

        idx = int(val)

        #if the new and old indices are the same, don't redraw.
        if idx == self.current_example_ind:
            return
        self.current_example_ind = idx
        self.fig.suptitle(f"Example {self.current_example_ind} / {len(self.task_data) - 1}")
        self.text_box.set_val(str(idx))
        self._plot_example()

    def _prev_example(self, _: str):
        """
        Event handler that handles requests to visualize the previous example.
        """

        idx = max(0, self.current_example_ind - 1)
        self.slider.set_val(idx)

    def _next_example(self, _: str):
        """
        Event handler that handles requests to visualize the next example.
        """

        idx = min(len(self.task_data) - 1, self.current_example_ind + 1)
        self.slider.set_val(idx)

    def _toggle_numbers(self, _: str):
        """
        Event handler that handles requests to show/hide the numbers on the matrix.
        """

        self.show_numbers = not self.show_numbers
        self._plot_example()

    def _text_submitted(self, val: str):
        """
        Event handler that handles requests to change the shown example via text input.

        Args:
            val (str): Index of the example to be shown.
        """

        if val.isdigit():
            idx = min(len(self.task_data) - 1, int(val))
            self.slider.set_val(idx)
    
    #=====Public API=====

    def show(self):
        """
        Shows figure.
        """
        plt.show()

if __name__ == "__main__":
    task_num = parse_visualization_args()
    task_name = f"task{task_num.zfill(3)}"

    TV_i = TaskVisualizer(task_name)
    TV_i.show()