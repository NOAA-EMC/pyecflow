"""Tests for anchor family generation functionality.

This module contains pytest tests for the WorkflowAnchorFamily class,
verifying that anchor families and their directories are created correctly
using the WorkflowSuite.add_anchor_family() method.
"""

# imports first
import os

import pyflow as pf

from pyecflow import WorkflowAnchorFamily, WorkflowSuite


# Default family structure for testing
DEFAULT_FAMILIES = {
    'family_A': ['family_Aa', 'family_Ab'],
    'family_B': ['family_Ba'],
}


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
        # waf = WorkflowAnchorFamily.generate_anchor_families(my_suite) #taking a suite
        WorkflowSuite.generate_anchor_families(my_suite, DEFAULT_FAMILIES) #pass in families to the suite

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

    def test_deploy_paths(self, tmp_path):
        """Test that tasks in anchor families get correct deploy paths.

        AnchorFamilies affect where .ecf files are deployed:
        - Tasks in anchor families: scripts/family_A/task_A1.ecf
        - Tasks in nested anchor families: scripts/family_A/family_Aa/task_Aa1.ecf
        """
        suite_dir = tmp_path / "testSuite"

        with WorkflowSuite('testSuite',
                           host=pf.LocalHost('localhost'),
                           files=str(suite_dir / 'scripts')) as my_suite:
            with pf.AnchorFamily('family_A') as fam_A:
                t1 = pf.Task('task_A1', script='echo A1')
                with pf.AnchorFamily('family_Aa'):
                    t2 = pf.Task('task_Aa1', script='echo Aa1')

        scripts_dir = str(suite_dir / 'scripts')
        assert t1.deploy_path == f"{scripts_dir}/family_A/task_A1.ecf"
        assert t2.deploy_path == f"{scripts_dir}/family_A/family_Aa/task_Aa1.ecf"

    def test_executable_children(self):
        """Test that executable_children returns only tasks and families."""
        with WorkflowSuite('testSuite', host=pf.LocalHost('localhost')) as my_suite:
            with pf.AnchorFamily('family_A') as fam_A:
                pf.Variable('VAR1', 'value1')
                t1 = pf.Task('task_A1', script='echo A1')
                with pf.AnchorFamily('family_Aa'):
                    t2 = pf.Task('task_Aa1', script='echo Aa1')
                t3 = pf.Task('task_A2', script='echo A2')

        children = fam_A.executable_children
        names = set([c.name for c in children])

        # Should include tasks and families, but NOT variables
        assert names == {'task_A1', 'family_Aa', 'task_A2'}

    def test_children_includes_all(self):
        """Test that children returns all direct children including variables."""
        with WorkflowSuite('testSuite', host=pf.LocalHost('localhost')) as my_suite:
            with pf.AnchorFamily('family_A') as fam_A:
                pf.Variable('VAR1', 'value1')
                t1 = pf.Task('task_A1', script='echo A1')
                with pf.AnchorFamily('family_Aa'):
                    t2 = pf.Task('task_Aa1', script='echo Aa1')

        children = fam_A.children
        names = set([c.name for c in children])

        # Should include everything: variables, tasks, families, and auto-generated attributes
        assert 'VAR1' in names
        assert 'task_A1' in names
        assert 'family_Aa' in names
