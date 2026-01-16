#import sys
import os
import pyflow as pf

def generate_suite(suite: pf.Suite, suite_dir: str = './', suite_name: str = 'test_suite'):
    """
    Generate an EcFlow suite definition file from a given pyflow Suite object and deploy the ecf scripts
    and include files to the suite directory. The suite directory is organized as follows:
    def/ - contains the suite definition file and also checks that the suite is valid
    include/ - contains any include files
    scripts/ - contains any ecf script files organized by families as subdirectories if applicable.

    Args:
        suite (pf.Suite): The pyflow Suite object to generate the EcFlow suite from.
        suite_dir (str): The directory where the suite definition and files will be deployed.
        suite_name (str): The name of the suite definition file (without extension).
        def_dir (str): The directory where the suite definition file will be deployed.
        include_dir (str): The directory where the include files will be deployed.
        scripts_dir (str): The directory where the ecf scripts will be deployed.
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
    #suite_def = suite.ecflow_definition()
    #suite_def.save_as_defs(os.path.join(def_dir, f'{suite_name}.def'))

    # Create include directory and copy header files
    if not os.path.exists(include_dir):
        os.makedirs(include_dir, exist_ok=True)

    # TODO: This needs to be implemented by methods in header.py from pyflow
    #for header_file in suite.headers:
    #    header_file_path = header_file.filepath
    #    if os.path.exists(header_file_path):
    #        shutil.copy(header_file_path, include_dir)

    # Create scripts directory and deploy scripts
    if not os.path.exists(scripts_dir):
        os.makedirs(scripts_dir, exist_ok=True)

    #suite.deploy_suite(scripts_dir)
    suite.deploy_suite()
    