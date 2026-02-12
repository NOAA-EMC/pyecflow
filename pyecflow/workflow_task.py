"""Workflow task module for pyecflow.

This module provides the WorkflowTask class for creating
tasks in ecFlow workflows.
"""

# imports
import pyflow as pf


class WorkflowTask(pf.Task):
    """A workflow task that extends pyflow's Task.

    This class represents a task in an ecFlow workflow. A task is the basic
    unit of work in ecFlow and represents a single job or script that needs
    to be executed. Tasks are created with a context dictionary that provides
    the necessary configuration including variables and the script to run.

    Parameters
    ----------
    name : str
        The name of the task.
    context : dict
        A dictionary containing task configuration with required keys:
        - 'variables' : dict
            Environment variables to set for the task.
        - 'script' : str
            Path to the script that the task will execute.
    **kwargs
        Additional keyword arguments to pass to the parent Task class.
    """

    def __init__(self, name: str, context: dict, **kwargs):
        super().__init__(name, variables=context['variables'], script=context['script'])
