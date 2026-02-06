"""Workflow anchor family module for pyecflow.

This module provides the WorkflowAnchorFamily class for creating
anchor families in ecFlow workflows.
"""

import pyflow as pf

# .workflow_task import WorkflowTask
from .workflow_task import WorkflowTask


class WorkflowAnchorFamily(pf.AnchorFamily):
    """A workflow anchor family that extends pyflow's AnchorFamily.

    This class represents an anchor family in an ecFlow workflow, which can
    contain multiple tasks. An anchor family is a special type of family that
    can be used to synchronize tasks across different parts of the workflow.

    Parameters
    ----------
    name : str
        The name of the anchor family.
    famAb_tasks : dict, optional
        A dictionary of tasks to add to the anchor family. Keys are task names
        and values are task configurations to pass to WorkflowTask.
        Default is None.
    **kwargs
        Additional keyword arguments to pass to the parent AnchorFamily class.

    Attributes
    ----------
    task_triggers : dict
        A dictionary mapping task names to their corresponding WorkflowTask
        objects that have been added to this anchor family.
    """

    # def __init__(self, name: str, famA_tasks: dict = None, **kwargs):
        # super().__init__(name)
        # task_triggers = {}

        # If famA_tasks is provided, create tasks from the dictionary
        # if famA_tasks is not None:
            # for tt in famA_tasks.keys():
                # task_tc = famA_tasks[tt]
                # task = WorkflowTask(tt, task_tc)
                # task_triggers[tt] = task
                # self.add(task)

        # self.task_triggers = task_triggers

    @staticmethod
    def generate_anchor_families(parent):
        """Generate the anchor family structure under a parent node.

        Creates a hierarchical structure of anchor families directly
        under the given parent:
        - family_A (with children family_Aa and family_Ab)
        - family_B (with child family_Ba)

        Parameters
        ----------
        parent : pf.Suite or pf.AnchorFamily
            The parent node to add anchor families to.
        """
        families = {
            'family_A': ['family_Aa', 'family_Ab'],
            'family_B': ['family_Ba'],
        }
        for fam_name, children in families.items():
            with parent:
                fam = pf.AnchorFamily(fam_name)
            for child_name in children:
                with fam:
                    pf.AnchorFamily(child_name)