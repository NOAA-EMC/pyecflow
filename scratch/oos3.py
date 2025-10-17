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
    with pf.Family('F') as f:
        MyTask('Seven', 7, defstatus=pf.state.suspended)
        MyTask('Five', 5)


class MyFamily(pf.Family):

    def __init__(self, name, counters, **kwargs):

        labels = {
            'total_counters': counters
        }

        super().__init__(name, labels=labels, **kwargs)

        with self:
            pf.sequence(MyTask('{}_{}'.format(name,i), i) for i in range(counters))

with pf.Suite('CountingSuite', files=os.path.join(filesdir, 'CountingSuite')) as s:
    f = MyFamily('TaskCounter', 7)

class CourseSuite(pf.Suite):
    """
    This CourseSuite object will be used throughout the course to provide sensible
    defaults without verbosity
    """
    def __init__(self, name, **kwargs):

        config = {
            'host': pf.LocalHost(),
            'files': os.path.join(filesdir, name),
            'home': outdir,
            'defstatus': pf.state.suspended
        }
        config.update(kwargs)

        super().__init__(name, **config)

with CourseSuite('configurable_suite') as s:
    MyFamily('fam1', 3)
    MyFamily('fam2', 5)

#s.check_definition()
print(s)
