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

#https://pyflow-workflow-generator.readthedocs.io/en/latest/content/introductory-course/script-handling.html
#The script attribute of the task (a Script object)
#Attributes of the Task object
#The execution host (which may be an attribute of the Task object, or one of its parents)
#The simplest example of a script can be seen below.

with pf.Suite('s', host=pf.LocalHost(), files='/s') as s:
    pf.Task('t', script='Running on $ECF_HOST')

s.deploy_suite(target=pf.Notebook)

# 1. Access to referenced ecFlow Variables (or other exportable objects, such as Repeats).
# 2. Manuals
# 3. Modules
# 4. Working directory information

with pf.Suite('s', host=pf.LocalHost(), files='/s', A_VARIABLE='has a value') as p:
    pf.Task('t',
            script='Running on $ECF_HOST\nVariable value $A_VARIABLE',
            manual="This is a multi-line manual\nwhich can contain instructions",
            workdir='/tmp/pyflow/s',
            modules=['ecbuild'])

s.deploy_suite(target=pf.Notebook)

t = pf.Task('t', script='echo "I am a simple script"')
print(type(t.script))
print(t.script)

t = pf.Task('t', script=[
    'echo "I am the first line"',
    'echo "I am the second line"\necho "and I am the third"'
])

print(type(t.script))
print(t.script)

class Config:
    debug = 1

config = Config()

#with pf.Suite('exporting', host=pf.LocalHost()) as y:
#    with pf.Task('mars', DEBUG=config.debug) as z:
#        t.script = pf.FileScript('sample_script.sh')
#        t.script.define_environment_variable("ENV1", 1234)
#        t.script.force_exported(t.DEBUG)

#s.check_definition()
print(s)
print(t)
print(p)
#print(y)
#s.deploy_suite()
#s.replace_on_server(server_host, server_port)