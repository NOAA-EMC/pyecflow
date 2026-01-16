# imports
import pyflow as pf


class WorkflowTask(pf.Task):
    def __init__(self, name: str, context: dict, **kwargs):
        super().__init__(name, variables=context['variables'], script=context['script'])
