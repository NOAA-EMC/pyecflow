"""Workflow suite module for pyecflow.

This module provides the WorkflowSuite class for creating
suites in ecFlow workflows.
"""

# imports
import pyflow as pf

# .workflow_task import WorkflowTask
from .workflow_task import WorkflowTask  # noqa: F401


class WorkflowSuite(pf.Suite):
    """A workflow suite that extends pyflow's Suite.

    This class represents a suite in an ecFlow workflow. A suite is the top-level
    container in the ecFlow hierarchy and can contain families and tasks. Each
    suite is independent and can be loaded and run separately.

    Parameters
    ----------
    name : str
        The name of the suite.
    *args
        Variable length argument list to pass to the parent Suite class.
    **kwargs
        Arbitrary keyword arguments to pass to the parent Suite class.
    """

    def __init__(self, name: str, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
