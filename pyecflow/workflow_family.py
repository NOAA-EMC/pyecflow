"""Workflow family module for pyecflow.

This module provides the WorkflowFamily class for creating
families in ecFlow workflows.
"""

# imports
import pyflow as pf

# .workflow_task import WorkflowTask
from .workflow_task import WorkflowTask  # noqa: F401


class WorkflowFamily(pf.Family):
    """A workflow family that extends pyflow's Family.

    This class represents a family in an ecFlow workflow, which is a container
    for tasks and other families. Families are used to organize and group
    related tasks in a workflow hierarchy.

    Parameters
    ----------
    name : str
        The name of the family.
    famAb_tasks : dict, optional
        A dictionary of tasks to add to the family. Keys are task names
        and values are task configurations to pass to WorkflowTask.
        Default is None.
    **kwargs
        Additional keyword arguments to pass to the parent Family class.

    Attributes
    ----------
    task_triggers : dict
        A dictionary mapping task names to their corresponding WorkflowTask
        objects that have been added to this family.
    """

    def __init__(self, name: str, famAb_tasks: dict = None, **kwargs):
        super().__init__(name)
        task_triggers = {}

        # If famAb_tasks is provided, create tasks from the dictionary
        if famAb_tasks is not None:
            for tt in famAb_tasks.keys():
                task_tc = famAb_tasks[tt]
                task = WorkflowTask(tt, task_tc)
                task_triggers[tt] = task
                self.add(task)

        self.task_triggers = task_triggers
