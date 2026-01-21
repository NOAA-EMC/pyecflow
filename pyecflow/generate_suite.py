"""Suite generation module for pyecflow.

This module provides functionality to generate ecFlow suite definition files
from pyflow Suite objects and deploy the associated scripts and include files
to a structured directory layout.
"""

# imports
import os

import pyflow as pf


def generate_suite(suite: pf.Suite, suite_dir: str = './', suite_name: str = 'test_suite'):
    """Generate an ecFlow suite definition file and deploy associated files.

    This function takes a pyflow Suite object and generates the necessary
    files and directory structure for an ecFlow suite. The suite directory
    is organized with subdirectories for definitions, include files, and
    scripts.

    Parameters
    ----------
    suite : pf.Suite
        The pyflow Suite object to generate the ecFlow suite from.
    suite_dir : str, optional
        The base directory where the suite files will be deployed.
        Default is './'.
    suite_name : str, optional
        The name of the suite definition file (without extension).
        Default is 'test_suite'.

    Notes
    -----
    The suite directory structure created is as follows:

    - def/ : Contains the suite definition file and validates the suite
    - include/ : Contains any include files (header files)
    - scripts/ : Contains ecf script files, organized by families as
      subdirectories if applicable

    The function performs the following operations:

    1. Creates the suite directory if it doesn't exist
    2. Creates subdirectories for def, include, and scripts
    3. Validates the suite definition with check_definition()
    4. Deploys suite scripts using deploy_suite()

    Examples
    --------
    >>> import pyflow as pf
    >>> suite = pf.Suite('my_suite')
    >>> generate_suite(suite, suite_dir='/path/to/suite', suite_name='my_suite')

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
    suite.check_definition()
    # suite_def = suite.ecflow_definition()
    # suite_def.save_as_defs(os.path.join(def_dir, f'{suite_name}.def'))

    # Create include directory and copy header files
    if not os.path.exists(include_dir):
        os.makedirs(include_dir, exist_ok=True)

    # TODO: This needs to be implemented by methods in header.py from pyflow
    # for header_file in suite.headers:
    #    header_file_path = header_file.filepath
    #    if os.path.exists(header_file_path):
    #        shutil.copy(header_file_path, include_dir)

    # Create scripts directory and deploy scripts
    if not os.path.exists(scripts_dir):
        os.makedirs(scripts_dir, exist_ok=True)

    # suite.deploy_suite(scripts_dir)
    suite.deploy_suite()
