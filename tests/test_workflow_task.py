"""Tests for WorkflowTask functionality.

This module contains pytest tests for the WorkflowTask class,
verifying that tasks are initialized correctly with their context
(variables and script), and that tasks are correctly added to
anchor families using WorkflowSuite.generate_tree().
"""

# imports first
import os
from pathlib import Path

import pyflow as pf
import yaml

from pyecflow import WorkflowSuite
from pyecflow.workflow_task import WorkflowTask

# Load test config from YAML file
_pyecflow_dir = Path(__file__).parent.parent / 'pyecflow'

with open(_pyecflow_dir / 'task_test_config.yaml') as f:
    task_test_dict = yaml.safe_load(f)


class TestYamlConfigLoading:
    """Test suite for YAML config file loading.

    Validates that the YAML config file exists and is loaded
    with the expected structure.
    """

    def test_task_test_dict_structure(self):
        """Test that task_test_dict loads with expected structure."""
        assert 'family_A' in task_test_dict
        assert 'family_B' in task_test_dict
        # Check tasks exist
        assert 'task_A1' in task_test_dict['family_A']['tasks']
        assert 'task_B1' in task_test_dict['family_B']['tasks']
        # Check nested structure
        assert 'family_Aa' in task_test_dict['family_A']['children']
        assert 'task_Aa1' in task_test_dict['family_A']['children']['family_Aa']['tasks']

    def test_task_config_has_required_keys(self):
        """Test that task configs have required 'variables' and 'script' keys."""
        task_A1 = task_test_dict['family_A']['tasks']['task_A1']
        assert 'variables' in task_A1
        assert 'script' in task_A1
        assert 'NUMBER' in task_A1['variables']
        assert task_A1['variables']['NUMBER'] == 1

    def test_yaml_file_exists(self):
        """Test that the YAML config file exists."""
        assert (_pyecflow_dir / 'task_test_config.yaml').exists()


class TestWorkflowTask:
    """Test suite for the WorkflowTask class.

    This test class validates the initialization and configuration
    of WorkflowTask instances, and verifies that tasks are correctly
    placed within anchor families.
    """

    def test_workflow_task_init(self):
        """Test that WorkflowTask initializes correctly with a context dictionary.

        This test verifies that a WorkflowTask can be created with a context
        containing variables and a script, and that these values are properly
        set on the task instance.
        """
        tAa1c = {'variables': {'NUMBER': 101},
                 'script': "echo family_Aa NUMBER=$NUMBER"}
        tAa1 = WorkflowTask('Aa1', tAa1c)
        print(tAa1.script)
        assert str(tAa1.script) == "echo family_Aa NUMBER=$NUMBER"
        assert tAa1.lookup_variable('NUMBER') == 101

    def test_task_children_exist(self, tmp_path):
        """Test that tasks are added to the correct anchor families.

        Verifies the task hierarchy:
        - family_A
          - family_Aa
            - task_Aa1
          - family_Ab
            - task_Ab1
            - task_Ab2
          - task_A1
        - family_B
          - family_Ba
            - task_Ba1
          - task_B1
        """
        suite_dir = tmp_path / "testSuite"
        print(f"\nSuite directory: {suite_dir}")

        my_suite = WorkflowSuite(
            'testSuite',
            host=pf.LocalHost('localhost'),
            files=str(suite_dir / 'scripts'))
        my_suite.generate_tree(task_test_dict)
        my_suite.generate_suite(suite_dir=suite_dir)

        # Print the .def file to show actual ecFlow node order
        def_file = suite_dir / 'def' / 'testSuite.def'
        print("\n--- ecFlow definition (shows actual order) ---")
        with open(def_file) as f:
            print(f.read())
        print("--- end of .def file ---")

        # Print the directory tree
        print("\nDirectory tree (filesystem order, NOT ecFlow order):")
        for root, dirs, files in os.walk(suite_dir):
            level = len(root.replace(str(suite_dir), '').split(os.sep)) - 1
            indent = '  ' * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = '  ' * (level + 1)
            for f in files:
                print(f"{subindent}{f}")

        # Check tasks exist on family_A
        assert my_suite.family_A.task_A1 is not None, "task_A1 was not created"
        assert my_suite.family_A.family_Aa.task_Aa1 is not None, "task_Aa1 was not created"
        assert my_suite.family_A.family_Ab.task_Ab1 is not None, "task_Ab1 was not created"
        assert my_suite.family_A.family_Ab.task_Ab2 is not None, "task_Ab2 was not created"

        # Check tasks exist on family_B
        assert my_suite.family_B.task_B1 is not None, "task_B1 was not created"
        assert my_suite.family_B.family_Ba.task_Ba1 is not None, "task_Ba1 was not created"

    def test_task_variables_exported(self, tmp_path):
        """Test that task variables are correctly set.

        Verifies each task has the expected NUMBER variable value.
        """
        suite_dir = tmp_path / "testSuite"

        my_suite = WorkflowSuite('testSuite',
                                 host=pf.LocalHost('localhost'),
                                 files=str(suite_dir / 'scripts'))
        my_suite.generate_tree(task_test_dict)
        my_suite.generate_suite(suite_dir=suite_dir)

        # Check variables on family_A tasks
        assert my_suite.family_A.task_A1.lookup_variable('NUMBER') == 1
        assert my_suite.family_A.family_Aa.task_Aa1.lookup_variable('NUMBER') == 11
        assert my_suite.family_A.family_Ab.task_Ab1.lookup_variable('NUMBER') == 21
        assert my_suite.family_A.family_Ab.task_Ab2.lookup_variable('NUMBER') == 22

        # Check variables on family_B tasks
        assert my_suite.family_B.task_B1.lookup_variable('NUMBER') == 1
        assert my_suite.family_B.family_Ba.task_Ba1.lookup_variable('NUMBER') == 11

    def test_task_ecf_files_created(self, tmp_path):
        """Test that .ecf script files are deployed for each task.

        Verifies the file structure:
        scripts/
          family_A/
            family_Aa/
              task_Aa1.ecf
            family_Ab/
              task_Ab1.ecf
              task_Ab2.ecf
            task_A1.ecf
          family_B/
            family_Ba/
              task_Ba1.ecf
            task_B1.ecf
        """
        suite_dir = tmp_path / "testSuite"
        print(f"\nSuite directory: {suite_dir}")

        my_suite = WorkflowSuite('testSuite',
                                 host=pf.LocalHost('localhost'),
                                 files=str(suite_dir / 'scripts'))
        my_suite.generate_tree(task_test_dict)
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

        scripts_dir = suite_dir / 'scripts'

        # Check .ecf files in family_A
        assert os.path.isfile(scripts_dir / 'family_A' / 'task_A1.ecf'), \
            "task_A1.ecf was not created"
        assert os.path.isfile(scripts_dir / 'family_A' / 'family_Aa' / 'task_Aa1.ecf'), \
            "task_Aa1.ecf was not created"
        assert os.path.isfile(scripts_dir / 'family_A' / 'family_Ab' / 'task_Ab1.ecf'), \
            "task_Ab1.ecf was not created"
        assert os.path.isfile(scripts_dir / 'family_A' / 'family_Ab' / 'task_Ab2.ecf'), \
            "task_Ab2.ecf was not created"

        # Check .ecf files in family_B
        assert os.path.isfile(scripts_dir / 'family_B' / 'task_B1.ecf'), \
            "task_B1.ecf was not created"
        assert os.path.isfile(scripts_dir / 'family_B' / 'family_Ba' / 'task_Ba1.ecf'), \
            "task_Ba1.ecf was not created"

        print("\nAll task .ecf files created successfully!")
