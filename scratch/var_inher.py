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

#with pf.Suite('hello_pyflow',
#              host=pf.LocalHost('localhost'),
#              files=filesdir,
#              home=outdir,
#              defstatus=pf.state.suspended) as s:
#    pf.Label('greeting', '')
#    t1 = pf.Task('t1', script='echo "I am on $(hostname) : $ECF_HOST"')
#    t2 = pf.Task('t2', script='ecflow_client --alter=change label greeting "Hello, pyflow!" /hello_pyflow')
#    t1 >> t2

#with pf.Suite('test') as s:
#    with pf.Family('f1'):
#        pf.Variable('SLEEP', 20)
#        pf.Task('t1')
#        pf.Task('t2')

"""
#Override variables furhter down the tree
with pf.Suite('test') as s:
    pf.Variable('SLEEP', 100)
    with pf.Family('f1'):
        pf.Variable('SLEEP', 80)
        pf.Task('t1')
        with pf.Task('t2'):
            pf.Variable('SLEEP', 9)
        with pf.Family('g1'):
            pf.Variable('SLEEP', 89)
            with pf.Task('x1'):
                pf.Variable('SLEEP', 10)
            pf.Task('x2')
    with pf.Family('f2'):
        pf.Task('t1')
        with pf.Task('t2'):
            pf.Variable('SLEEP', 77)
        with pf.Family('g2'):
            with pf.Task('x1'):
                pf.Variable('SLEEP', 12)
            pf.Task('x2')
"""

with pf.Suite('s') as s:
    with pf.Family('f'):
        pf.Edit(FOO='foo_value', BAR='bar_value')

#s.check_definition()
print(s)

#s.deploy_suite()
#s.replace_on_server(server_host, server_port)

