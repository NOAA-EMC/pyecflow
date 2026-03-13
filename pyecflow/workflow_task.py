"""Workflow task module for pyecflow.

This module provides the WorkflowTask class for creating tasks in ecFlow
workflows. Include files (head.h, tail.h) are required by ecFlow and managed
by workflow_include.py. The optional envir-p1.h (NCO extension) is only
included when explicitly configured.

The generated .ecf files use the traditional ecFlow %include approach:
    %include <head.h>
    %include <envir-p1.h>  # only if configured
    # script content
    %include <tail.h>

Classes
-------
WorkflowTask
    A workflow task for ecFlow suites.
"""

# imports
import pyflow as pf


class WorkflowTask(pf.Task):
    # Docstring intentionally omitted to prevent pyflow from using it as %manual.
    # See module docstring for class documentation.
    #
    # Include files (head.h, tail.h) are required. envir-p1.h is optional (NCO extension).
    # This class overrides generate_script to use traditional %include directives.
    #
    # Parameters:
    #   name : str - The name of the task.
    #   context : dict - Task configuration with 'variables', 'script', optional 'manual', 'envir'.
    #   **kwargs - Additional keyword arguments to pass to the parent Task class.

    # Class attribute: whether to include envir-p1.h in generated scripts.
    # Set by WorkflowSuite based on config. Default False (opt-in).
    _include_envir = False

    def __init__(self, name: str, context: dict, **kwargs):
        # Get script content, prepending any environment setup
        script = context.get('script', '')
        envir = context.get('envir', '')
        if envir:
            script = f"{envir}\n\n{script}"

        # Get manual from context, default to empty string to suppress class docstring
        manual = context.get('manual', '')

        super().__init__(
            name,
            variables=context.get('variables', {}),
            script=script,
            manual=manual,
            **kwargs,
        )

    def generate_script(self):
        """Generate .ecf script with traditional %include directives.

        Produces a script in this exact order:
            1. #!/bin/bash shebang
            2. %include <head.h>
            3. %include <envir-p1.h> (only if _include_envir is True)
            4. Script content (wrapped in %nopp/%end)
            5. %include <tail.h>
            6. %manual section (optional, only if task has manual content)

        Returns:
            tuple: (lines, headers) where lines is list of script lines
                   and headers is empty list (includes handled inline).
        """
        # Generate script content using parent's stub generation
        try:
            script = self.generate_stub([self.script])
        except Exception as e:
            raise RuntimeError(
                f"Failed to generate script for {self.fullname}"
            ) from e

        manual = self.generate_stub(self.manual)

        lines = []

        # Shebang
        lines += ["#!/bin/bash", ""]

        # Required ecFlow header
        lines += ["%include <head.h>"]

        # Optional NCO envir-p1.h (only if configured)
        if self._include_envir:
            lines += ["%include <envir-p1.h>"]

        lines += [""]

        # Script content wrapped in %nopp/%end (no preprocessing)
        lines += ["%nopp", ""]
        lines += script
        lines += ["", "%end", ""]

        # Tail include
        lines += ["%include <tail.h>", ""]

        # Add manual section only if content exists
        # Manual content is already wrapped in %manual/%end by generate_stub
        if manual:
            lines += manual
            lines += [""]

        # Return empty headers list since we handle includes directly
        return lines, []
