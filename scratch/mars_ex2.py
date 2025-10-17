ars_task_script = """
req=$(mktemp req.XXXX)
cat > $req <<@
{{ REQUEST }}
@
mars $req
rm $req
"""


class MarsTask(pf.Task):

    verb = None

    def __init__(self, request_dict, **kwargs):

        # Construct a MarsRequest object from the dictionary supplied
        assert self.verb is not None
        request = MarsRequest(self.verb, request_dict)

        name = kwargs.get('name', "{}_data".format(self.verb))

        super().__init__(name,
                         labels={'info': ''},
                         script=pf.TemplateScript(mars_task_script, REQUEST=request),
                         **kwargs)

        self.script.define_environment_variable('MARS_ECFLOW_LABEL', self.info)
        self.script.define_environment_variable('MARS_TIMERS_FILE', "{}.timers".format(name))


class ArchiveTask(MarsTask):
    verb = 'archive'


class RetrieveTask(MarsTask):
    verb = 'retrieve'
