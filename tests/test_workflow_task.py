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
_test_data_dir = Path(__file__).parent / 'data'

with open(_test_data_dir / 'task_test_config.yaml') as f:
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
        assert (_test_data_dir / 'task_test_config.yaml').exists()


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
        set on the task instance. Include files (head.h, tail.h, envir-p1.h) are
        managed separately by workflow_include.py.
        """
        tAa1c = {'variables': {'NUMBER': 101},
                 'script': "echo family_Aa NUMBER=$NUMBER"}
        tAa1 = WorkflowTask('Aa1', tAa1c)
        print(tAa1.script)

        # Verify the script contains the user script
        script_str = str(tAa1.script)
        assert "echo family_Aa NUMBER=$NUMBER" in script_str

        # Verify variable is set correctly
        assert tAa1.lookup_variable('NUMBER') == 101

    def test_workflow_task_generate_script_format(self, tmp_path):
        """Test that generate_script produces correct %include directive order.

        Verifies the .ecf file format follows the traditional ecFlow pattern:
            1. #!/bin/bash shebang
            2. %include <head.h>
            3. %include <envir-p1.h> (only if configured)
            4. %nopp / script content / %end
            5. %include <tail.h>
            6. %manual section (only if task has manual content)
        """
        suite_dir = tmp_path / "testSuite"

        my_suite = WorkflowSuite('testSuite',
                                 host=pf.LocalHost('localhost'),
                                 files=str(suite_dir / 'scripts'))

        with my_suite:
            task = WorkflowTask('test_task', {
                'script': 'echo "Hello World"',
                'variables': {'VAR1': 'value1'}
            })
            lines, headers = task.generate_script()

        script_content = '\n'.join(lines)
        print(f"\nGenerated script:\n{script_content}")

        # Verify headers list is empty (includes handled inline)
        assert headers == [], "Headers should be empty since includes are inline"

        # Verify correct order of elements
        shebang_pos = script_content.find('#!/bin/bash')
        head_pos = script_content.find('%include <head.h>')
        nopp_pos = script_content.find('%nopp')
        script_pos = script_content.find('echo "Hello World"')
        end_pos = script_content.find('%end')
        tail_pos = script_content.find('%include <tail.h>')

        # Required elements must be present
        assert shebang_pos >= 0, "Shebang not found"
        assert head_pos >= 0, "head.h include not found"
        assert nopp_pos >= 0, "%nopp not found"
        assert script_pos >= 0, "Script content not found"
        assert end_pos >= 0, "%end not found"
        assert tail_pos >= 0, "tail.h include not found"

        # envir-p1.h should NOT be present (opt-in only, not configured)
        envir_pos = script_content.find('%include <envir-p1.h>')
        assert envir_pos == -1, "envir-p1.h should not be present unless configured"

        # %manual should NOT be present (no manual content provided)
        manual_pos = script_content.find('%manual')
        assert manual_pos == -1, "%manual should not be present when no manual content"

        # Verify correct order
        assert shebang_pos < head_pos, "Shebang must come before head.h"
        assert head_pos < nopp_pos, "head.h must come before %nopp"
        assert nopp_pos < script_pos, "%nopp must come before script content"
        assert script_pos < end_pos, "Script content must come before %end"
        assert end_pos < tail_pos, "%end must come before tail.h"

        print("\nAll %include directives in correct order!")

    def test_workflow_task_with_envir_configured(self, tmp_path):
        """Test that envir-p1.h is included when configured.

        When the includes.envir path is set in config, the generated .ecf
        should include %include <envir-p1.h> between head.h and %nopp.
        """
        suite_dir = tmp_path / "testSuite"
        custom_envir = tmp_path / "envir-p1.h"
        custom_envir.write_text("# Custom envir")

        config = {
            'includes': {
                'envir': str(custom_envir)
            },
            'family_A': {
                'tasks': {
                    'task_A1': {
                        'script': 'echo test',
                        'variables': {'VAR': '1'}
                    }
                }
            }
        }

        my_suite = WorkflowSuite('testSuite',
                                 host=pf.LocalHost('localhost'),
                                 files=str(suite_dir / 'scripts'))
        my_suite.generate_tree(config)
        my_suite.generate_suite(suite_dir=str(suite_dir))

        # Read the generated .ecf file
        ecf_file = suite_dir / 'scripts' / 'family_A' / 'task_A1.ecf'
        script_content = ecf_file.read_text()
        print(f"\nGenerated script with envir:\n{script_content}")

        # Verify envir-p1.h is included
        assert '%include <envir-p1.h>' in script_content, "envir-p1.h should be included when configured"

        # Verify correct order
        head_pos = script_content.find('%include <head.h>')
        envir_pos = script_content.find('%include <envir-p1.h>')
        nopp_pos = script_content.find('%nopp')

        assert head_pos < envir_pos, "head.h must come before envir-p1.h"
        assert envir_pos < nopp_pos, "envir-p1.h must come before %nopp"

        print("\nenvir-p1.h correctly included when configured!")

    def test_workflow_task_manual_placement(self, tmp_path):
        """Test that %manual section appears after %include <tail.h>.

        When a task has a manual, it should be placed at the end of the .ecf file
        after the tail include, wrapped in %manual/%end directives.
        """
        suite_dir = tmp_path / "testSuite"

        my_suite = WorkflowSuite('testSuite',
                                 host=pf.LocalHost('localhost'),
                                 files=str(suite_dir / 'scripts'))

        with my_suite:
            task = WorkflowTask('test_task', {
                'script': 'echo "Hello World"',
                'variables': {'VAR1': 'value1'},
                'manual': 'This is the manual page for the task.\nIt explains what the task does.'
            })
            lines, headers = task.generate_script()

        script_content = '\n'.join(lines)
        print(f"\nGenerated script with manual:\n{script_content}")

        # Verify %manual appears after %include <tail.h>
        tail_pos = script_content.find('%include <tail.h>')
        manual_pos = script_content.find('%manual')

        assert tail_pos >= 0, "tail.h include not found"
        assert manual_pos >= 0, "%manual not found"
        assert tail_pos < manual_pos, "%manual must come after %include <tail.h>"

        # Verify manual content is present
        assert "This is the manual page for the task." in script_content
        assert "It explains what the task does." in script_content

        # Verify %manual is closed with %end
        # Find the %end that closes %manual (should be after the manual content)
        manual_content_pos = script_content.find("This is the manual page")
        end_after_manual = script_content.find('%end', manual_content_pos)
        assert end_after_manual > manual_content_pos, "%end must close the %manual section"

        print("\n%manual section correctly placed after tail.h!")

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
