import pyflow as pf
import pytest  # noqa: F401

import pyecflow as pef


class TestWorkflowTask:
    def test_nodes_task1(self):
        with pf.Suite("test_suite") as suite:
            with pf.Family("test_family") as family:
                task = pef.WorkflowTask(name="test_task")
        assert task.name == "test_task"
        script = task.generate_script()
        #print(script)
        print(script)
