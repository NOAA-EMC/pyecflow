import os
from pwd import getpwuid

import pyflow as pf

class Cleanup(pf.Task):
    def __init__(self, path, name='cleanup', **kwargs):
        assert path != "/"
        super().__init__(name, script='rm -rf "{}"'.format(path), **kwargs)


class TestBase(pf.AnchorFamily):

    """This class is an interface"""

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

        # Generate a unique working directory
        self._workdir = os.path.join(self.host.scratch_directory,
                                     self.suite.name, self.fullname.replace('/', '_'))

        # Ensure that the data gets put somewhere
        self._data_filename = 'retrieved.grib'
        request = self.request_dict().copy()
        request['target'] = self._data_filename

        with self:
            (
                RetrieveTask(request, workdir=self._workdir)
                >>
                self.build_test()
                >>
                Cleanup(self._workdir)
            )

    def request_dict(self):
        raise NotImplementedError("abstract base property")

    def build_test(self):
        raise NotImplementedError("abstract base method")

class GribLsTest(TestBase):
    def __init__(self, date, param, **kwargs):
        self._date = date
        self._param = param
        name = kwargs.pop('name', 'grib_ls')
        super().__init__(name, **kwargs)

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

    def build_test(self):
        return pf.Task('grib_ls', workdir=self._workdir, script='grib_ls -m {}'.format(self._data_filename))


class LsTest(TestBase):
    def __init__(self, **kwargs):
        super().__init__('ls', **kwargs)

    def request_dict(self):
        return {
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

    def build_test(self):
        with pf.Family('test_family') as f:
            pf.Task('ls', workdir=self._workdir, script='ls -l {}'.format(self._data_filename))
        return f

with CourseSuite('inheritance_example') as s:
    with pf.Family('tests'):
        (
            GribLsTest(datetime.date.today() - datetime.timedelta(days=2), 't')
            >>
            GribLsTest(datetime.date.today() - datetime.timedelta(days=1), 'z', name='grib_ls_2')
            >>
            LsTest()
        )

s