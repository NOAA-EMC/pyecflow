"""Workflow task module for pyecflow.

This module provides the WorkflowTask class for creating tasks in ecFlow
workflows. Header files (head.h, tail.h, envir-p1.h) are managed by
workflow_header.py and deployed to the suite's include/ directory.

Classes
-------
WorkflowTask
    A workflow task for ecFlow suites.
"""

# imports
import pyflow as pf


class WorkflowTask(pf.Task):
    # Docstring intentionally omitted to prevent pyflow from using it as %manual.
    # See module docstring for class documentation.
    #
    # Headers (head.h, tail.h, envir-p1.h) are deployed by workflow_header.py.
    # pyflow generates %include <head.h> and %include <tail.h> directives.
    #
    # Parameters:
    #   name : str - The name of the task.
    #   context : dict - Task configuration with 'variables', 'script', optional 'manual', 'envir'.
    #   **kwargs - Additional keyword arguments to pass to the parent Task class.

    def __init__(self, name: str, context: dict, **kwargs):
        # Get script content, prepending any environment setup
        script = context.get('script', '')
        envir = context.get('envir', '')
        if envir:
            script = f"{envir}\n\n{script}"

        # Get manual from context, default to empty string to suppress class docstring
        manual = context.get('manual', '')

        super().__init__(
            name,
            variables=context.get('variables', {}),
            script=script,
            manual=manual,
            **kwargs,
        )
