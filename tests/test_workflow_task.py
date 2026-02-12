"""Tests for WorkflowTask functionality.

This module contains pytest tests for the WorkflowTask class,
verifying that tasks are initialized correctly with their context
(variables and script), and that tasks are correctly added to
anchor families using WorkflowSuite.generate_tasks().
"""

# imports first
import os

import pyflow as pf

from pyecflow import WorkflowSuite
from pyecflow.workflow_task import WorkflowTask

# Default family structure for testing
DEFAULT_FAMILIES = {
    'family_A': ['family_Aa', 'family_Ab'],
    'family_B': ['family_Ba'],
}

# Default task structure for testing
DEFAULT_TASKS = {
    'family_A': {
        'tasks': {
            'task_A1': {
                'variables': {'NUMBER': 1},
                'script': 'echo family_A task_A1 NUMBER=$NUMBER',
            },
        },
        'children': {
            'family_Aa': {
                'tasks': {
                    'task_Aa1': {
                        'variables': {'NUMBER': 11},
                        'script': 'echo family_Aa task_Aa1 NUMBER=$NUMBER',
                    },
                },
            },
            'family_Ab': {
                'tasks': {
                    'task_Ab1': {
                        'variables': {'NUMBER': 21},
                        'script': 'echo family_Ab task_Ab1 NUMBER=$NUMBER',
                    },
                    'task_Ab2': {
                        'variables': {'NUMBER': 22},
                        'script': 'echo family_Ab task_Ab2 NUMBER=$NUMBER',
                    },
                },
            },
        },
    },
    'family_B': {
        'tasks': {
            'task_B1': {
                'variables': {'NUMBER': 1},
                'script': 'echo family_B task_B1 NUMBER=$NUMBER',
            },
        },
        'children': {
            'family_Ba': {
                'tasks': {
                    'task_Ba1': {
                        'variables': {'NUMBER': 11},
                        'script': 'echo family_Ba task_Ba1 NUMBER=$NUMBER',
                    },
                },
            },
        },
    },
}


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

        my_suite = WorkflowSuite('testSuite',
                                 host=pf.LocalHost('localhost'),
                                 files=str(suite_dir / 'scripts'))
        families = my_suite.add_anchor_family(DEFAULT_FAMILIES)
        WorkflowSuite.generate_tasks(families, DEFAULT_TASKS)
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
        families = my_suite.add_anchor_family(DEFAULT_FAMILIES)
        WorkflowSuite.generate_tasks(families, DEFAULT_TASKS)
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
        families = my_suite.add_anchor_family(DEFAULT_FAMILIES)
        WorkflowSuite.generate_tasks(families, DEFAULT_TASKS)
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
