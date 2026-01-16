# imports
import pyflow as pf
# .workflow_task import WorkflowTask
from .workflow_task import WorkflowTask


class WorkflowFamily(pf.Family):
    def __init__(self, name: str, famAb_tasks: dict = None, **kwargs):
        super().__init__(name)
        task_triggers = {}
