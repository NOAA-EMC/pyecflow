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

with CourseSuite('family_example') as s:
with pf.Suite('family_example') as s:
    with pf.Family('simple', labels={'example': ''}) as f:
        LabelSetter((f.example, 'example text'))
    MyFamily('derived_family', 5)

#with CourseSuite('anchor_families', files=filesdir) as s:
with pf.Suite('anchor_families', files=filesdir) as s:
    with pf.Family('f1'):
        pf.Task('test1')        # Script <files>/test1.ecf
    with pf.Family('f2'):
        pf.Task('test1')        # Script <files>/test1.ecf
    with pf.AnchorFamily('f'):
        with pf.Family('f1'):
            pf.Task('test1')    # Script <files>/f/test1.ecf
            pf.Task('test2')    # Script <files>/f/test2.ecf
        with pf.Family('f2'):
            pf.Task('test2')    # Script <files>/f/test2.ecf

#s.check_definition()
print(s)

#s.deploy_suite()
#s.replace_on_server(server_host, server_port)
