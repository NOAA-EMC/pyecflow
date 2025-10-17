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

with pf.Suite('test') as s:
    with pf.Family('f1'):
        pf.Variable('SLEEP', 20)
        t1 = pf.Task('t1')
        t2 = pf.Task('t2')

    t1 >> t2

with pf.Suite('test', host=pf.LocalHost(), files='/test') as t:
    with pf.Family('f1'):
        pf.Variable('SLEEP', 20)
        pf.Task('t1')
        pf.Task('t2', script='ecflow_client --wait="t1 == complete"')

with pf.Suite('test', host=pf.LocalHost(), files='/test') as u:
    with pf.Family('f1'):
        pf.Variable('SLEEP', 20)
        t1 = pf.Task('t1')
        with pf.Task('t2', script=[
            'echo "I will now sleep for %SLEEP% seconds"',
            'sleep %SLEEP%',
            'ecflow_client --event=a    # Set the first event',
            'sleep %SLEEP%              # Sleep a bit more',
            'ecflow_client --event=b    # Set the second event',
            'sleep %SLEEP%              # A last nap...',
        ]) as t2:
            pf.Event('a')
            pf.Event('b')
        t3 = pf.Task('t3')
        t4 = pf.Task('t4')

    t2.triggers = t1
    t3.triggers = t2.a
    t4.triggers = t2.b

with pf.Suite('test', host=pf.LocalHost(), files='/test') as v:
    with pf.Family('f1'):
        pf.Variable('SLEEP', 20)
        t1 = pf.Task('t1')
        with pf.Task('t2', script=[
            'echo "I will now sleep for %SLEEP% seconds"',
            'sleep %SLEEP%',
            'ecflow_client --event=a    # Set the first event',
            'sleep %SLEEP%              # Sleep a bit more',
            'ecflow_client --event=b    # Set the second event',
            'sleep %SLEEP%              # A last nap...',
        ]) as t2:
            pf.Event('a')
            pf.Event('b')
        t3 = pf.Task('t3')
        t4 = pf.Task('t4')

    t2.triggers = t1
    t3.triggers = t2.a
    t4.completes = t2.b
    t4.triggers = t2
"""
with pf.Suite('s') as a:

    with pf.Family('repeat1') as repeat1:
        pf.RepeatDate('YMD', datetime.date(2019, 1, 1), datetime.date(2019, 12, 31))

    with pf.Family('repeat2') as repeat2:
        pf.RepeatDate('YMD', datetime.date(2019, 1, 1), datetime.date(2019, 12, 31))

    repeat2.triggers = (repeat1 == pf.state.complete) | (repeat1.YMD > repeat2.YMD)

    pf.Task('t3').completes = (repeat2.YMD > '20190616')

with pf.Suite('s') as x:

    with pf.Family('repeat1') as repeat1:
        pf.RepeatDate('YMD', datetime.date(2019, 1, 1), datetime.date(2019, 12, 31))

    with pf.Family('repeat2') as repeat2:
        pf.RepeatDate('YMD', datetime.date(2019, 1, 1), datetime.date(2019, 12, 31))

    repeat2.triggers = (repeat1 == pf.state.complete) | (repeat1.YMD > repeat2.YMD)

    pf.Task('t3').completes = (repeat2.YMD > '20190616')

with pf.Suite('s') as y:
    t1 = MyTask('t1')
    t2 = MyTask('t2')
    t3 = MyTask('t3')

    t1.triggers = t2.complete & t3.aborted

with pf.Suite('s') as z:
    t1 = MyTask('t1')
    t2 = MyTask('t2')
    t3 = MyTask('t3')

    t1.triggers = t2.complete
    t1.triggers |= t3.aborted

with pf.Suite('s') as s:
    t1 = MyTask('t1')
    t2 = MyTask('t2')
    t2.triggers = t1.complete

with pf.Suite('s') as s:
    t1 = MyTask('t1')
    t2 = MyTask('t2')
    t2.triggers = (t1 == pf.state.complete)

with pf.Suite('s') as s:
    t1 = MyTask('t1')
    t2 = MyTask('t2')
    t1 >> t2

with pf.Suite("s") as s:
    (
        MyTask('t1')
        >>
        MyTask('t2')
    )
"""

class LabelSetter(pf.Task):

    def __init__(self, *args, **kwargs):
        """
        Accepts a sequence of label-value tuples
        """
        script = [
            pf.TemplateScript(
                'ecflow_client --alter=change label {{ LABEL.name }} "{{ VALUE }}" {{ LABEL.parent.fullname }}',
                LABEL=label, VALUE=value
            ) for label, value in args
        ]

        name = kwargs.pop('name', 'set_labels')
        super().__init__(name, script=script, **kwargs)


class WaitSeconds(pf.Task):
    def __init__(self, seconds, **kwargs):
        name = kwargs.pop('name', 'wait_{}'.format(seconds))
        super().__init__(name, script='sleep {}'.format(seconds), **kwargs)


with CourseSuite('looping_constructs') as c:

    with pf.Family('date_family'):
        pf.RepeatDate('REPEAT_DATE',
                      datetime.date(year=2019, month=1, day=1),
                      datetime.date(year=2019, month=12, day=31))

        with pf.Family('hour_family', labels={'date_time': ''}) as f:
            pf.RepeatInteger('REPEAT_HOUR', 1, 24)
            (
                LabelSetter((f.date_time, '$REPEAT_DATE hour $REPEAT_HOUR'))
                >>
                WaitSeconds(2)
            )

#s.check_definition()
print('basic trigger:')
print(s)
print('embedded trigger:')
print(t)
print('Events:')
print(u)
print('Complete:')
print(v)
print('Expressions:')
#print(a)
#print(x)
#print('Combined Expressions:')
#print(y)
print('class LabelSetter:')
print(c)

#s.deploy_suite()
#s.replace_on_server(server_host, server_port)
