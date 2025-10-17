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

with pf.Suite('test', host=pf.LocalHost(), files='/test') as r:
    with pf.Family('label'):
        with pf.Task('t1', script=[
            'n=1',
            'while [[ $n -le 5 ]]                   # Loop 5 times',
            'do',
            '    msg=\"The date is now $(date)\"',
            '    ecflow_client --label=info \"$msg\"  # Set the label',
            '    sleep 60                           # Wait a one minute',
            '    (( n = $n + 1 ))',
            'done',
            '',
            'ecflow_client --label=info \"I have now finished my work.\"',
        ]) as t1:
            pf.Label('info', '')

with pf.Suite('test', host=pf.LocalHost(), files='/test') as s:
    with pf.Family('f1'):
        pf.Variable('SLEEP', 20)
        with pf.Task('t1') as t1:
            pf.Meter('progress', 1, 100, 90)
        with pf.Task('t2', script=[
            'echo "I will now sleep for %SLEEP% seconds"',
            'sleep %SLEEP%',
            'n=1',
            'while [[ $n -le 100 ]]                   # Loop 100 times',
            'do',
            '    sleep 1                              # Wait a short time',
            '    ecflow_client --meter=progress $n    # Notify ecFlow',
            '    (( n = $n + 1 ))',
            'done',
        ]) as t2:
            pf.Event('a')
            pf.Event('b')
        t3 = pf.Task('t3')
        t4 = pf.Task('t4')
        t5 = pf.Task('t5')
        t6 = pf.Task('t6')
        t7 = pf.Task('t7')

    t2.triggers = t1
    t3.triggers = t2.a
    t4.completes = t2.b
    t4.triggers = t2
    t5.triggers = t1.progress >= 30
    t6.triggers = t1.progress >= 60
    t7.triggers = t1.progress >= 90

print('meters:')
print(s)

#s.deploy_suite()
#s.replace_on_server(server_host, server_port)
