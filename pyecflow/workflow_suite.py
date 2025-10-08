from __future__ import absolute_import

import pyflow as pf


class WorkflowSuite(pf.Suite):
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
