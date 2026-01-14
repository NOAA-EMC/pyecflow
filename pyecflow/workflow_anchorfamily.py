import pyflow as pf
#.workflow_task import WorkflowTask
from .workflow_task import WorkflowTask

class WorkflowAnchorFamily(pf.AnchorFamily):
    #def __init__(self, name: str, famAb_tasks: dict, **kwargs):
        #super().__init__(name, variables=context['variables'])
    def __init__(self, name: str, famAb_tasks: dict = None, **kwargs):
        super().__init__(name)
        task_triggers = {}
        #for tt in famAb_tasks.keys(): #should a dict., keys are tasks, tt is the key 
        #    task_tc= famAb_tasks[tt] #get the context dict for this task
            #task_triggers[tt] = WorkflowTask(tt, task_tc)
        #    task = WorkflowTask(tt, task_tc)
        #    task_triggers[tt] = task
        #    self.add(task)
        
        # If famAb_tasks is provided, create tasks from the dictionary
        if famAb_tasks is not None:
            for tt in famAb_tasks.keys():
                task_tc = famAb_tasks[tt]
                task = WorkflowTask(tt, task_tc)
                task_triggers[tt] = task
                self.add(task)
        
        self.task_triggers = task_triggers