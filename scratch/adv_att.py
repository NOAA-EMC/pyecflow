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

with pf.Suite('s', host=pf.NullHost()) as s:
    with pf.Family('f') as f:
        pf.Label('l', 'text')
        pf.Variable('V', 'value')

class DerivedFamily(pf.Family):
    def __init__(self):
        super().__init__('f')
        with self:
            pf.Label('l', 'text')
            pf.Variable('V', 'value')

with pf.Suite('s', host=pf.NullHost()) as t:
    DerivedFamily()

with pf.Suite('s', host=pf.NullHost()) as u:
    pf.Family('f', labels={'l': 'text'}, V='value')

class DerivedFamily(pf.Family):
    def __init__(self, **kwargs):

        variables = {'V': 'value'}
        variables.update(kwargs)

        labels = {'l': 'text'}

        super().__init__('f', labels=labels, **variables)


with pf.Suite('s', host=pf.NullHost()) as y:
    DerivedFamily()

with pf.Suite('s', host=pf.NullHost()) as w:
    f = pf.Family('f')
    f.V = 'value'

#Access properties of EcFlow vars:
with pf.Suite('s'):
    v = pf.Variable('A_VARIABLE', 1234)

print(str(v), repr(v), v.value)
print(v.name, v.fullname)


#s.check_definition()
print('pyflow obj made with suite method:')
print(s)
print('pyflow obj made with class obj:')
print(t)
print('pyflow obj made with kwargs on parent node constructor:')
print(u)
print('Attributes w/ one instance are lowercase string of attribute class.\nAttributes w/ multiple instances are pluralized lower case of attribute class.\nEcFlow variables are kwargs and capitalized var names.')
print(y)
print('unambigous objects (variables, script, etc.) can be set as attributes on node objects.')
print(w)
#s.deploy_suite()
#s.replace_on_server(server_host, server_port)
