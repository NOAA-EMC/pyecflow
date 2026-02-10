from pyecflow.workflow_task import WorkflowTask


class TestWorkflowTask:

    def test_workflow_task_init(self):
        tAa1c = {'variables': {'NUMBER': 101},
                 'script': "echo family_Aa NUMBER=$NUMBER"}
        tAa1 = WorkflowTask('Aa1', tAa1c)
        # print(dir(tAa1))
        print(tAa1.script)
        assert str(tAa1.script) == "echo family_Aa NUMBER=$NUMBER"
        assert tAa1.lookup_variable('NUMBER') == 101


#    def test_init_calls_super_with_name_variables_and_script(monkeypatch):
#        captured = {}
#
#        def fake_init(self, *args, **kwargs):
#            captured['args'] = args
#            captured['kwargs'] = kwargs
#
#        monkeypatch.setattr(workflow_task.pf.Task, '__init__', fake_init, raising=True)
#
#        ctx = {'variables': {'x': 1}, 'script': 'run.sh'}
#        inst = workflow_task.WorkflowTask('mytask', ctx, extra_kw=123)
#
#        assert isinstance(inst, workflow_task.pf.Task)
#        assert captured['args'] == ('mytask',)
#        assert captured['kwargs'] == {'variables': ctx['variables'], 'script': ctx['script']}
#        # extra_kw should not be forwarded to the super initializer
#        assert 'extra_kw' not in captured['kwargs']
#
#
#    def test_missing_variables_raises_key_error():
#        ctx = {'script': 'run.sh'}
#        with pytest.raises(KeyError):
#            workflow_task.WorkflowTask('t', ctx)
#
#
#    def test_missing_script_raises_key_error():
#        ctx = {'variables': {}}
#        with pytest.raises(KeyError):
#            workflow_task.WorkflowTask('t', ctx)
