"""Tests for anchor family generation functionality.

This module contains pytest tests for the WorkflowAnchorFamily class,
verifying that anchor families and their directories are created correctly
using the WorkflowSuite.add_anchor_family() method.
"""

# imports first
import os

import pyflow as pf

from pyecflow import WorkflowAnchorFamily, WorkflowSuite


class TestGenerateAnchorFamily:
    """Test suite for the WorkflowAnchorFamily class.

    This test class validates the functionality of the WorkflowAnchorFamily
    class, ensuring that it correctly creates the necessary anchor family
    structure.
    """

    def test_anchor_family_children_exist(self, tmp_path):
        """Test that anchor family children are created correctly.

        Verifies the hierarchy:
        - family_A
          - family_Aa
          - family_Ab
        - family_B
          - family_Ba
        """
        suite_dir = tmp_path / "testSuite"
        print(f"\nSuite directory: {suite_dir}")

        my_suite = WorkflowSuite('testSuite',
                                 host=pf.LocalHost('localhost'),
                                 files=str(suite_dir / 'scripts'))
        my_suite.add_anchor_family()
        my_suite.generate_suite(suite_dir=suite_dir)

        # Print the directory tree
        print("\nDirectory tree:")
        for root, dirs, files in os.walk(suite_dir):
            level = len(root.replace(str(suite_dir), '').split(os.sep)) - 1
            indent = '  ' * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = '  ' * (level + 1)
            for f in files:
                print(f"{subindent}{f}")

        # Check family_A and its children
        fam_A = my_suite.family_A
        assert fam_A is not None, "family_A was not created"
        assert fam_A.family_Aa is not None, "family_Aa was not created"
        assert fam_A.family_Ab is not None, "family_Ab was not created"

        # Check family_B and its child
        fam_B = my_suite.family_B
        assert fam_B is not None, "family_B was not created"
        assert fam_B.family_Ba is not None, "family_Ba was not created"

    def test_anchor_family_directories_created(self, tmp_path):
        """Test that anchor family directories are created when suite is generated.

        Verifies the directory structure:
        def/
          testSuite.def
        include/
        scripts/
          family_A/
            family_Aa/
            family_Ab/
          family_B/
            family_Ba/
        """
        suite_dir = tmp_path / "testSuite"
        print(f"\nSuite directory: {suite_dir}")

        my_suite = WorkflowSuite('testSuite',
                                 host=pf.LocalHost('localhost'),
                                 files=str(suite_dir / 'scripts'))
        my_suite.add_anchor_family()
        my_suite.generate_suite(suite_dir=suite_dir)

        # Print the directory tree
        print("\nDirectory tree:")
        for root, dirs, files in os.walk(suite_dir):
            level = len(root.replace(str(suite_dir), '').split(os.sep)) - 1
            indent = '  ' * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = '  ' * (level + 1)
            for f in files:
                print(f"{subindent}{f}")

        # Check def directory and .def file
        assert os.path.isdir(suite_dir / 'def'), "def/ directory was not created"
        assert os.path.isfile(suite_dir / 'def' / 'testSuite.def'), "testSuite.def was not created"

        # Check include directory
        assert os.path.isdir(suite_dir / 'include'), "include/ directory was not created"

        # Check scripts directory
        scripts_dir = suite_dir / 'scripts'
        assert os.path.isdir(scripts_dir), "scripts/ directory was not created"

        # Check family_A and its children
        assert os.path.isdir(scripts_dir / 'family_A'), "family_A/ directory was not created"
        assert os.path.isdir(scripts_dir / 'family_A' / 'family_Aa'), "family_Aa/ directory was not created"
        assert os.path.isdir(scripts_dir / 'family_A' / 'family_Ab'), "family_Ab/ directory was not created"

        # Check family_B and its child
        assert os.path.isdir(scripts_dir / 'family_B'), "family_B/ directory was not created"
        assert os.path.isdir(scripts_dir / 'family_B' / 'family_Ba'), "family_Ba/ directory was not created"

        print("\nAll anchor family directories created successfully!")
