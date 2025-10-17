import os
from pwd import getpwuid

import pyflow as pf


class DelegatingTest(pf.AnchorFamily):
    def __init__(self, config, **kwargs):

        name = config.name
        super().__init__(name, **kwargs)

        # Generate a unique working directory
        workdir = os.path.join(self.host.scratch_directory,
                               self.suite.name, self.fullname.replace('/', '_'))

        # Ensure that the data gets put somewhere
        data_filename = 'retrieved.grib'
        request = config.request_dict.copy()
        request['target'] = data_filename

        with self:
            (
                RetrieveTask(request, workdir=workdir)
                >>
                config.build_test(workdir, data_filename)
                >>
                Cleanup(workdir)
            )

class LsConfig:
    name = 'ls'
    request_dict = {
        'class': 'od',
        'expver': '0001',
        'stream': 'oper',
        'date': -1,
        'time': [0, 12],
        'step': 0,
        'type': 'an',
        'levtype': 'ml',
        'levelist': 1,
        'param': 't',
    }

    @staticmethod
    def build_test(workdir, data_filename):
        with pf.Family('test_family') as f:
            return pf.Task('ls', workdir=workdir, script='ls -l {}'.format(data_filename))


class GribLsConfig:

    def __init__(self, date, param, name='grib_ls'):
        self.name = name
        self._date = date
        self._param = param

    @property
    def request_dict(self):
        return {
            'class': 'od',
            'expver': '0001',
            'stream': 'oper',
            'date': self._date,
            'time': [0, 12],
            'step': 0,
            'type': 'an',
            'levtype': 'ml',
            'levelist': 1,
            'param': self._param,
        }

    def build_test(self, workdir, data_filename):
        return pf.Task('grib_ls', workdir=workdir, script='grib_ls -m {}'.format(data_filename))


class CombinedConfig:
    def __init__(self):
        self.tests = [
            GribLsConfig(datetime.date.today() - datetime.timedelta(days=2), 't'),
            GribLsConfig(datetime.date.today() - datetime.timedelta(days=1), 'z', name='grib_ls_2'),
            LsConfig # n.b. here we just used a raw class.
        ]

class DelegatedSuite(CourseSuite):
    def __init__(self, config):
        super().__init__('delegated_example')

        with self:
            pf.sequence(DelegatingTest(test_cfg) for test_cfg in config.tests)


s = DelegatedSuite(CombinedConfig())
s