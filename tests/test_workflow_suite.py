"""Tests for suite generation functionality.

This module contains pytest tests for the WorkflowSuite.generate_suite() method,
verifying that suite directories and files are created correctly.
"""

# imports first
import os

import pyflow as pf

from pyecflow import WorkflowSuite


class TestGenerateSuite:
    """Test suite for the WorkflowSuite.generate_suite() method.

    This test class validates the functionality of the WorkflowSuite.generate_suite()
    method, ensuring that it correctly creates the necessary directory
    structure for ecFlow suites.
    """

    # def test_generate_suite_creates_directories(self):
    def test_generate_suite_creates_directories(self, tmp_path):
        """Test that WorkflowSuite.generate_suite() creates the required directory structure.

        This test verifies that the WorkflowSuite.generate_suite() method creates the
        following directories:
        - def/ : For suite definition files
        - include/ : For include/header files
        - scripts/ : For ecFlow script files

        The test also verifies that the created paths are actual directories
        and not files.

        Notes
        -----
        This test creates a minimal test suite and uses a pytest temporary
        directory (tmp_path / "testSuite") as the target directory. The test
        validates both the existence and type (directory) of the created paths.
        """

# Create a minimal suite for testing
        suite_dir = tmp_path / "testSuite"

        my_suite = WorkflowSuite('testSuite',
                                 host=pf.LocalHost('localhost'),
                                 files=str(suite_dir / 'scripts'))

        # Generate the suite
        my_suite.generate_suite(suite_dir=suite_dir)

        # Assert that the directories were created
        assert os.path.exists(suite_dir / 'def'), "def/ directory was not created"
        assert os.path.exists(suite_dir / 'include'), "include/ directory was not created"
        assert os.path.exists(suite_dir / 'scripts'), "scripts/ directory was not created"

        # Assert that they are directories
        assert os.path.isdir(suite_dir / 'def'), "def/ is not a directory"
        assert os.path.isdir(suite_dir / 'include'), "include/ is not a directory"
        assert os.path.isdir(suite_dir / 'scripts'), "scripts/ is not a directory"
