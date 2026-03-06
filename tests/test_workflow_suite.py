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

        The method also recursively creates directories for any families and nested
        families that have been added to the suite.

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
        print(f"\nSuite directory: {suite_dir}")

        my_suite = WorkflowSuite('testSuite',
                                 host=pf.LocalHost('localhost'),
                                 files=str(suite_dir / 'scripts'))

        # Generate the suite
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

        # Assert that the directories were created
        assert os.path.exists(suite_dir / 'def'), "def/ directory was not created"
        assert os.path.exists(suite_dir / 'include'), "include/ directory was not created"
        assert os.path.exists(suite_dir / 'scripts'), "scripts/ directory was not created"

        # Assert that they are directories
        assert os.path.isdir(suite_dir / 'def'), "def/ is not a directory"
        assert os.path.isdir(suite_dir / 'include'), "include/ is not a directory"
        assert os.path.isdir(suite_dir / 'scripts'), "scripts/ is not a directory"


class TestHeaderConfiguration:
    """Test suite for header file configuration via YAML config."""

    def test_default_headers_copied(self, tmp_path):
        """Test that default headers are copied when no headers config provided."""
        suite_dir = tmp_path / "testSuite"

        config = {
            'family_A': {
                'tasks': {
                    'task_A1': {
                        'variables': {'VAR': '1'},
                        'script': 'echo test'
                    }
                }
            }
        }

        my_suite = WorkflowSuite(
            'testSuite',
            host=pf.LocalHost('localhost'),
            files=str(suite_dir / 'scripts')
        )
        my_suite.generate_tree(config)
        my_suite.generate_suite(suite_dir=str(suite_dir))

        # Check that default headers were copied
        include_dir = suite_dir / 'include'
        assert (include_dir / 'head.h').exists()
        assert (include_dir / 'tail.h').exists()
        assert (include_dir / 'envir-p1.h').exists()

        # Check content contains expected markers from default files
        head_content = (include_dir / 'head.h').read_text()
        assert 'ECF_NAME' in head_content

    def test_custom_head_path_from_config(self, tmp_path):
        """Test that custom head.h path from config is used."""
        suite_dir = tmp_path / "testSuite"
        custom_head = tmp_path / "custom_head.h"
        custom_head.write_text("# Custom head file\necho 'Custom head'")

        config = {
            'headers': {
                'head': str(custom_head)
            },
            'family_A': {
                'tasks': {
                    'task_A1': {
                        'variables': {'VAR': '1'},
                        'script': 'echo test'
                    }
                }
            }
        }

        my_suite = WorkflowSuite(
            'testSuite',
            host=pf.LocalHost('localhost'),
            files=str(suite_dir / 'scripts')
        )
        my_suite.generate_tree(config)
        my_suite.generate_suite(suite_dir=str(suite_dir))

        # Check custom head was used
        head_content = (suite_dir / 'include' / 'head.h').read_text()
        assert "Custom head file" in head_content

        # Check default files were used for others
        tail_content = (suite_dir / 'include' / 'tail.h').read_text()
        assert 'ecflow_client' in tail_content

    def test_all_custom_headers_from_config(self, tmp_path):
        """Test that all custom header paths from config are used."""
        suite_dir = tmp_path / "testSuite"

        # Create custom header files
        custom_head = tmp_path / "custom_head.h"
        custom_tail = tmp_path / "custom_tail.h"
        custom_envir = tmp_path / "custom_envir.h"

        custom_head.write_text("# Custom head")
        custom_tail.write_text("# Custom tail")
        custom_envir.write_text("# Custom envir")

        config = {
            'headers': {
                'head': str(custom_head),
                'tail': str(custom_tail),
                'envir': str(custom_envir)
            },
            'family_A': {
                'tasks': {
                    'task_A1': {
                        'variables': {'VAR': '1'},
                        'script': 'echo test'
                    }
                }
            }
        }

        my_suite = WorkflowSuite(
            'testSuite',
            host=pf.LocalHost('localhost'),
            files=str(suite_dir / 'scripts')
        )
        my_suite.generate_tree(config)
        my_suite.generate_suite(suite_dir=str(suite_dir))

        include_dir = suite_dir / 'include'
        assert (include_dir / 'head.h').read_text() == "# Custom head"
        assert (include_dir / 'tail.h').read_text() == "# Custom tail"
        assert (include_dir / 'envir-p1.h').read_text() == "# Custom envir"

    def test_empty_header_paths_use_defaults(self, tmp_path):
        """Test that empty header paths in config use defaults."""
        suite_dir = tmp_path / "testSuite"

        config = {
            'headers': {
                'head': '',  # Empty string should use default
                'tail': None,  # None should use default
                # envir not specified - should use default
            },
            'family_A': {
                'tasks': {
                    'task_A1': {
                        'variables': {'VAR': '1'},
                        'script': 'echo test'
                    }
                }
            }
        }

        my_suite = WorkflowSuite(
            'testSuite',
            host=pf.LocalHost('localhost'),
            files=str(suite_dir / 'scripts')
        )
        my_suite.generate_tree(config)
        my_suite.generate_suite(suite_dir=str(suite_dir))

        # All should use defaults
        include_dir = suite_dir / 'include'
        head_content = (include_dir / 'head.h').read_text()
        assert 'ECF_NAME' in head_content  # Default head.h marker

    def test_headers_config_not_treated_as_family(self, tmp_path):
        """Test that 'headers' key is not treated as a family name."""
        suite_dir = tmp_path / "testSuite"

        config = {
            'headers': {
                'head': None
            },
            'family_A': {
                'tasks': {
                    'task_A1': {
                        'variables': {'VAR': '1'},
                        'script': 'echo test'
                    }
                }
            }
        }

        my_suite = WorkflowSuite(
            'testSuite',
            host=pf.LocalHost('localhost'),
            files=str(suite_dir / 'scripts')
        )
        families = my_suite.generate_tree(config)

        # 'headers' should not appear as a family
        assert 'headers' not in families
        assert 'family_A' in families
