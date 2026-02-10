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

    # Default task structure for testing/development
    DEFAULT_TASKS = {
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

    @staticmethod
    def generate_tasks(suite, tasks=None):
        """Add tasks to the anchor families in the suite.

        Creates WorkflowTask instances within each anchor family
        based on the task dictionary. The anchor families must already
        exist on the suite before calling this method.

        Child families are processed before tasks at each level, ensuring
        that in the ecFlow definition, nested families appear before
        sibling tasks.

        Parameters
        ----------
        suite : pf.Suite
            The suite containing the anchor families to add tasks to.
        tasks : dict, optional
            Dictionary mapping family names to their task/children config.
            If None, uses DEFAULT_TASKS.

        Examples
        --------
        >>> # Using default structure
        >>> WorkflowTask.generate_tasks(suite)

        >>> # Using custom structure from config
        >>> config = load_yaml('tasks.yml')
        >>> WorkflowTask.generate_tasks(suite, config)
        """
        if tasks is None:
            tasks = WorkflowTask.DEFAULT_TASKS

        WorkflowTask._add_tasks_to_families(suite, tasks)

    @staticmethod
    def _add_tasks_to_families(parent, family_tasks):
        """Recursively add tasks to existing anchor families.

        Processes child families before adding tasks at each level to ensure
        proper ordering in the ecFlow definition (children appear before
        sibling tasks).

        Parameters
        ----------
        parent : pf.Suite or pf.AnchorFamily
            The parent node containing the families.
        family_tasks : dict
            Dictionary mapping family names to their task/children config.
        """
        for fam_name, fam_config in family_tasks.items():
            fam = getattr(parent, fam_name)
            # Recurse into child families first
            children = fam_config.get('children', {})
            if children:
                WorkflowTask._add_tasks_to_families(fam, children)
            # Add tasks to this family after children
            for task_name, task_context in fam_config.get('tasks', {}).items():
                with fam:
                    WorkflowTask(task_name, task_context)
