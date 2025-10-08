from __future__ import absolute_import

import pyflow as pf


class WorkflowTask(pf.Task):
    def __init__(self,
                 name: str,
                 script: str | list = [],
                 variables: dict = {},
                 *args, **kwargs):

        # Provide a default script if none is given
        if not script:
            script = [
                '#!/bin/bash',
                f'echo "This is a default script named {name}"'
            ]

        super().__init__(name, script=script, variables=variables, *args, **kwargs)
        
        heads, tails = self.headers
        print(heads, tails)


    def generate_script(self):
        """Instead of using the pyflow.Task.generate_script method, we override it to construct our own script
        based on the template provided and the necessary task attributes.
        """

        if isinstance(self.script, list):
            return "\n".join(self.script)
        return self.script
