# imports first
import os
import tempfile
import pyflow as pf
from pyecflow.generate_suite import generate_suite


class TestGenerateSuite:

    def test_generate_suite_creates_directories(self):
        """
        Test the generate_suite function to create suite directories. These pytests check if
        def/, include/ and scripts/ directories are created correctly.
        """
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            suite_dir = os.path.join(temp_dir, 'testSuite')

            # Create a simple test suite
            with pf.Suite('testSuite',
                          host=pf.LocalHost('localhost'),
                          files=os.path.join(suite_dir, 'scripts')) as test_suite:
                pass

            # Generate the suite
            generate_suite(test_suite, suite_dir=suite_dir)

            # Assert that the directories were created
            assert os.path.exists(os.path.join(suite_dir, 'def')), "def/ directory was not created"
            assert os.path.exists(os.path.join(suite_dir, 'include')), "include/ directory was not created"
            assert os.path.exists(os.path.join(suite_dir, 'scripts')), "scripts/ directory was not created"

            # Assert that they are directories
            assert os.path.isdir(os.path.join(suite_dir, 'def')), "def/ is not a directory"
            assert os.path.isdir(os.path.join(suite_dir, 'include')), "include/ is not a directory"
            assert os.path.isdir(os.path.join(suite_dir, 'scripts')), "scripts/ is not a directory"
