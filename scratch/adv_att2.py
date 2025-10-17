import os
from pwd import getpwuid

import pyflow as pf


scratchdir = os.path.join(os.path.abspath(''), 'scratch')
filesdir = os.path.join(scratchdir, 'files')
outdir = os.path.join(scratchdir, 'out')

if not os.path.exists(filesdir):
    os.makedirs(filesdir, exist_ok=True)

if not os.path.exists(outdir):
    os.makedirs(outdir, exist_ok=True)

passwd = getpwuid(os.getuid())

server_host = 'localhost'
server_port = 1500+passwd.pw_uid
"""
with pf.Suite('s') as s:
    with pf.Family('family1') as f1:
        pf.Label('the_label', '')

    with pf.Family('family2') as f2:
        LabelSetter((f1.the_label, "a value"), name='labeller')

print(f2.labeller.script)

#accessing children of various nodes as attributes of the parent.
with pf.Suite('s') as s:
    with pf.Family('family1') as f1:
        pf.Label('the_label', '')

    with pf.Family('family2') as f2:
        LabelSetter((f1.the_label, "a value"), name='labeller')

print(f2.labeller.script)
"""
class ChildTask(pf.Task):
    def __init__(self, external_variable):
        script = pf.TemplateScript(
            'echo "external variable: {{ VARIABLE }}"',
            VARIABLE=external_variable
        )
        super().__init__('uses_var', script=script)

with CourseSuite('templated_external_variable') as s:
    with pf.Family('containing_family', MY_VAR=1234) as f:
        ChildTask(f.MY_VAR)

#s.check_definition()
print(s)

#s.deploy_suite()
#s.replace_on_server(server_host, server_port)
