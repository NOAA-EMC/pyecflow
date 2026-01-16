# imports
import pyflow as pf
# .workflow_task import WorkflowTask
from .workflow_task import WorkflowTask


class WorkflowSuite(pf.Suite):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
