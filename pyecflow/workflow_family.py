# imports
import pyflow as pf
# .workflow_task import WorkflowTask
from .workflow_task import WorkflowTask  # noqa: F401


class WorkflowFamily(pf.Family):
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
