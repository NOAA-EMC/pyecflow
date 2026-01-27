"""Workflow suite module for pyecflow.

This module provides the WorkflowSuite class for creating
suites in ecFlow workflows.
"""

# imports
import os

import pyflow as pf


class WorkflowSuite(pf.Suite):
    """A workflow suite that extends pyflow's Suite.

    This class represents a suite in an ecFlow workflow. A suite is the top-level
    container in the ecFlow hierarchy and can contain families and tasks. Each
    suite is independent and can be loaded and run separately.

    Parameters
    ----------
    name : str
        The name of the suite.
    *args
        Variable length argument list to pass to the parent Suite class.
    **kwargs
        Arbitrary keyword arguments to pass to the parent Suite class.
    """

    def __init__(self, name: str, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

    def generate_suite(self, suite_dir: str = './'):
        """Generate an ecFlow suite definition file and deploy associated files.

        This method generates the necessary files and directory structure for
        an ecFlow suite. The suite directory is organized with subdirectories
        for definitions, include files, and scripts.

        Parameters
        ----------
        suite_dir : str, optional
            The base directory where the suite files will be deployed.
            Default is './'.

        Notes
        -----
        The suite directory structure created is as follows:

        - def/ : Contains the suite definition file and validates the suite
        - include/ : Contains any include files (header files)
        - scripts/ : Contains ecf script files, organized by families as
          subdirectories if applicable

        The method performs the following operations:

        1. Creates the suite directory if it doesn't exist
        2. Creates subdirectories for def, include, and scripts
        3. Validates the suite definition with check_definition()
        4. Deploys suite scripts using deploy_suite()

        Examples
        --------
        >>> suite = WorkflowSuite('my_suite')
        >>> suite.generate_suite(suite_dir='/path/to/suite')

        This will create the following structure:
        /path/to/suite/
            def/
            include/
            scripts/
        """
        # Ensure the suite directory exists
        if not os.path.exists(suite_dir):
            os.makedirs(suite_dir, exist_ok=True)

        # Define directory paths
        scripts_dir = os.path.join(suite_dir, 'scripts')
        include_dir = os.path.join(suite_dir, 'include')
        def_dir = os.path.join(suite_dir, 'def')

        # Create def directory
        if not os.path.exists(def_dir):
            os.makedirs(def_dir, exist_ok=True)

        # Save the suite definition file
        self.check_definition()

        # Create include directory and copy header files
        if not os.path.exists(include_dir):
            os.makedirs(include_dir, exist_ok=True)

        # TODO: This needs to be implemented by methods in header.py from pyflow
        # for header_file in self.headers:
        #    header_file_path = header_file.filepath
        #    if os.path.exists(header_file_path):
        #        shutil.copy(header_file_path, include_dir)

        # Create scripts directory and deploy scripts
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir, exist_ok=True)

        self.deploy_suite()
