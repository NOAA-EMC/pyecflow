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

#This demonstrates a number of characteristics of object-oriented suite design:
#Functionality that is configurable on a data description.
#Functionality that is encapsulated in re-usable subcomponents
#Delegation or inheritance to fine-tune behaviour within an existing framework
#Firstly we create a helper class that can understand MARS requests, and output them in a useful format.

class MarsRequest:

    separator = ",\n    "

    def __init__(self, verb, request_dict):
        self._verb = verb
        self._request_dict = request_dict

    def __str__(self):
        return (
            self._verb +
            self.separator +
            self.separator.join("{}={}".format(k, self._resolve(v)) for k, v in self._request_dict.items())
        )

    @staticmethod
    def _resolve(v):
        '''Convert values into something understood by MARS'''
        if isinstance(v, bool):
            return "on" if v else "off"
        if isinstance(v, list):
            return '/'.join(MarsRequest._resolve(vv) for vv in v)
        if isinstance(v, str) and ('/' in v or '$' in v):
            return '"{}"'.format(v)
        return str(v)
