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

    @staticmethod
    def generate_tasks(suite):
        """Add tasks to the anchor families in the suite.

        Creates WorkflowTask instances within each anchor family
        based on the task dictionary. The anchor families must already
        exist on the suite before calling this method.

        The resulting task placement is:

        - family_A/task_A1
        - family_A/family_Aa/task_Aa1
        - family_A/family_Ab/task_Ab1
        - family_A/family_Ab/task_Ab2
        - family_B/task_B1
        - family_B/family_Ba/task_Ba1

        Parameters
        ----------
        suite : pf.Suite
            The suite containing the anchor families to add tasks to.
        """
        tasks = {
            'family_A': {
                'tasks': {
                    'task_A1': {
                        'variables': {'NUMBER': 1},
                        'script': 'echo family_A task_A1 NUMBER=$NUMBER',
                    },
                },
                'children': {
                    'family_Aa': {
                        'tasks': {
                            'task_Aa1': {
                                'variables': {'NUMBER': 11},
                                'script': 'echo family_Aa task_Aa1 NUMBER=$NUMBER',
                            },
                        },
                    },
                    'family_Ab': {
                        'tasks': {
                            'task_Ab1': {
                                'variables': {'NUMBER': 21},
                                'script': 'echo family_Ab task_Ab1 NUMBER=$NUMBER',
                            },
                            'task_Ab2': {
                                'variables': {'NUMBER': 22},
                                'script': 'echo family_Ab task_Ab2 NUMBER=$NUMBER',
                            },
                        },
                    },
                },
            },
            'family_B': {
                'tasks': {
                    'task_B1': {
                        'variables': {'NUMBER': 1},
                        'script': 'echo family_B task_B1 NUMBER=$NUMBER',
                    },
                },
                'children': {
                    'family_Ba': {
                        'tasks': {
                            'task_Ba1': {
                                'variables': {'NUMBER': 11},
                                'script': 'echo family_Ba task_Ba1 NUMBER=$NUMBER',
                            },
                        },
                    },
                },
            },
        }
        WorkflowTask._add_tasks_to_families(suite, tasks)

    @staticmethod
    def _add_tasks_to_families(parent, family_tasks):
        """Recursively add tasks to existing anchor families.

        Parameters
        ----------
        parent : pf.Suite or pf.AnchorFamily
            The parent node containing the families.
        family_tasks : dict
            Dictionary mapping family names to their task/children config.
        """
        for fam_name, fam_config in family_tasks.items():
            fam = getattr(parent, fam_name)
            # Add tasks to this family
            for task_name, task_context in fam_config.get('tasks', {}).items():
                with fam:
                    WorkflowTask(task_name, task_context)
            # Recurse into child families
            children = fam_config.get('children', {})
            if children:
                WorkflowTask._add_tasks_to_families(fam, children)

