"""Tests for suite generation functionality.

This module contains pytest tests for the generate_suite function,
verifying that suite directories and files are created correctly.
"""

# imports first
import os

import pyflow as pf

from pyecflow.generate_suite import generate_suite

# set up server
server_host = 'localhost'
server_port = 22921  # Anna's personal Ursa EcFlow server port


class TestGenerateSuite:
    """Test suite for the generate_suite function.

    This test class validates the functionality of the generate_suite
    function, ensuring that it correctly creates the necessary directory
    structure for ecFlow suites.
    """

    def test_generate_suite_creates_directories(self):
        """Test that generate_suite creates the required directory structure.

        This test verifies that the generate_suite function creates the
        following directories:
        - def/ : For suite definition files
        - include/ : For include/header files
        - scripts/ : For ecFlow script files

        The test also verifies that the created paths are actual directories
        and not files.

        Notes
        -----
        This test creates a minimal test suite and uses './testSuite' as
        the target directory. The test validates both the existence and
        type (directory) of the created paths.
        """

# Create a minimal suite for testing
        suite_dir = './testSuite'

        with pf.Suite('testSuite',
                      host=pf.LocalHost('localhost'),
                      files='./testSuite/scripts') as my_suite:
            pass

        # Generate the suite
        generate_suite(my_suite, suite_dir=suite_dir)
        # generate_suite(test_suite, suite_dir=suite_dir)

        # Assert that the directories were created
        assert os.path.exists(os.path.join(suite_dir, 'def')), "def/ directory was not created"
        assert os.path.exists(os.path.join(suite_dir, 'include')), "include/ directory was not created"
        assert os.path.exists(os.path.join(suite_dir, 'scripts')), "scripts/ directory was not created"

        # Assert that they are directories
        assert os.path.isdir(os.path.join(suite_dir, 'def')), "def/ is not a directory"
        assert os.path.isdir(os.path.join(suite_dir, 'include')), "include/ is not a directory"
        assert os.path.isdir(os.path.join(suite_dir, 'scripts')), "scripts/ is not a directory"
