from __future__ import absolute_import

import pyflow as pf


class WorkflowFamily(pf.Family):
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
