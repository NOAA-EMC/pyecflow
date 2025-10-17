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

with pf.Suite('first_suite') as s:

    with pf.Family('family1') as f1:
        t1 = pf.Task('t1')
        with pf.Task('t2') as t2:
            pf.Variable('FOO', 'bar')

        t1 >> t2

    with pf.Family('family2') as f2:
        t1 = pf.Task('t1')
        t2 = pf.Task('t2')
        t1 >> t2

    f1 >> f2

with pf.Family('f') as f:

    variables = {
        'HALF': 7,
        'LIMIT': 2*7
    }

    labels = {
        'a_label': 'with a value'
    }

    t = pf.Task('my_task', labels=labels, defstatus=pf.state.suspended, variables=variables)

    # Note that t is incomplete at this point...
    t.script = [
        'echo "This is a counting task ..."',
        'for i in $(seq 1 $HALF); do echo "count $i/$LIMIT"; done',
        'i=$[$HALF+1]; while [ $i -lt $LIMIT ]; do echo "count $i/$LIMIT" ; i=$[$i+1]; done'
    ]

class MyTask(pf.Task):

    """Counts to the double of a number, first half using a for loop then a while loop"""

    def __init__(self, name, default_value=0, **kwargs):

        variables = {
            'HALF': default_value,
            'LIMIT': 2*default_value,
        }
        variables.update(kwargs.pop('variables', {}))

        labels = {
            'counter_label': 'count to {}'.format(2*default_value)
        }

        script = [
            'echo "This is a counting task named {}"'.format(name),
            'for i in $(seq 1 $HALF); do echo "count $i/$LIMIT"; done',
            'i=$[$HALF+1]; while [ $i -lt $LIMIT ]; do echo "count $i/$LIMIT" ; i=$[$i+1]; done'
        ]

        super().__init__(name,
                         script=script,
                         labels=labels,
                         variables=variables,
                         **kwargs)

with pf.Suite('CountingSuite', files=os.path.join(filesdir, 'CountingSuite')) as s:
    with pf.Family('F') as h:
        MyTask('Seven', 7, defstatus=pf.state.suspended)
        MyTask('Five', 5)

#s.check_definition()
print("Procedural Program:")
print(s)
print("\nNon-OO Task: ")
print(f)
print("\nOO Task: ")
print(h)

#s.deploy_suite()
#s.replace_on_server(server_host, server_port)
