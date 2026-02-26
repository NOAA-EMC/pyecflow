"""Tests for anchor family generation functionality.

This module contains pytest tests for the WorkflowAnchorFamily class,
verifying that anchor families and their directories are created correctly
using the WorkflowSuite.generate_tree() method.
"""

# imports first
import os
from pathlib import Path

import pyflow as pf
import yaml

from pyecflow import WorkflowSuite
from pyecflow.workflow_anchorfamily import WorkflowAnchorFamily

# Load test configs from YAML files
_test_data_dir = Path(__file__).parent / 'data'

with open(_test_data_dir / 'fam_test_config.yaml') as f:
    fam_test_config = yaml.safe_load(f)

with open(_test_data_dir / 'duplicate_name_config.yaml') as f:
    duplicate_name_config = yaml.safe_load(f)


class TestYamlConfigLoading:
    """Test suite for YAML config file loading.

    Validates that the YAML config files exist and are loaded
    with the expected structure.
    """

    def test_fam_test_config_structure(self):
        """Test that fam_test_config loads with expected structure."""
        assert 'family_A' in fam_test_config
        assert 'family_B' in fam_test_config
        assert 'children' in fam_test_config['family_A']
        assert 'family_Aa' in fam_test_config['family_A']['children']
        assert 'family_Ab' in fam_test_config['family_A']['children']
        assert 'family_Ba' in fam_test_config['family_B']['children']

    def test_duplicate_name_config_structure(self):
        """Test that duplicate_name_config loads with expected structure."""
        assert 'family_A' in duplicate_name_config
        assert 'family_B' in duplicate_name_config
        assert 'shared_child' in duplicate_name_config['family_A']['children']
        assert 'shared_child' in duplicate_name_config['family_B']['children']

    def test_yaml_files_exist(self):
        """Test that the YAML config files exist."""
        assert (_test_data_dir / 'fam_test_config.yaml').exists()
        assert (_test_data_dir / 'duplicate_name_config.yaml').exists()


class TestWorkflowAnchorFamily:
    """Test suite for the WorkflowAnchorFamily class.

    This test class validates the initialization and configuration
    of WorkflowAnchorFamily instances.
    """

    def test_workflow_anchor_family_init_with_context(self):
        """Test that WorkflowAnchorFamily initializes correctly with a context.

        This test verifies that a WorkflowAnchorFamily can be created with a
        context containing variables, and that these values are properly
        set on the family instance.
        """
        # AnchorFamily requires a Suite context
        with WorkflowSuite('testSuite', host=pf.LocalHost('localhost')):
            context = {'variables': {'ENV': 'production', 'LEVEL': 1}}
            family = WorkflowAnchorFamily('test_family', context)
            assert family.name == 'test_family'
            assert family.lookup_variable('ENV') == 'production'
            assert family.lookup_variable('LEVEL') == 1

    def test_workflow_anchor_family_init_without_context(self):
        """Test that WorkflowAnchorFamily initializes correctly without a context.

        This test verifies that a WorkflowAnchorFamily can be created without
        a context dictionary.
        """
        # AnchorFamily requires a Suite context
        with WorkflowSuite('testSuite', host=pf.LocalHost('localhost')):
            family = WorkflowAnchorFamily('test_family')
            assert family.name == 'test_family'

    def test_workflow_anchor_family_init_empty_context(self):
        """Test that WorkflowAnchorFamily handles empty context correctly.

        This test verifies that a WorkflowAnchorFamily can be created with
        an empty context dictionary.
        """
        # AnchorFamily requires a Suite context
        with WorkflowSuite('testSuite', host=pf.LocalHost('localhost')):
            family = WorkflowAnchorFamily('test_family', {})
            assert family.name == 'test_family'


class TestGenerateAnchorFamily:
    """Test suite for anchor family generation.

    This test class validates the functionality of WorkflowSuite.generate_tree()
    for creating anchor families, ensuring that it correctly creates the
    necessary family structure from a nested configuration dictionary.
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
        my_suite.generate_tree(fam_test_config)

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

    def test_created_families_match_hierarchy(self, tmp_path):
        """Test that generate_tree() creates all families from the config.

        Uses _extract_family_hierarchy() to get expected families and
        validates that generate_tree() returns matching family objects.
        """
        suite_dir = tmp_path / "testSuite"

        my_suite = WorkflowSuite('testSuite',
                                 host=pf.LocalHost('localhost'),
                                 files=str(suite_dir / 'scripts'))

        # Get expected families from config
        expected_families = set(
            WorkflowSuite._extract_family_hierarchy(fam_test_config).keys()
        )

        # Generate tree and get created families
        created_families = my_suite.generate_tree(fam_test_config)

        # Validate all expected families were created
        assert set(created_families.keys()) == expected_families, \
            f"Family mismatch: expected {expected_families}, got {set(created_families.keys())}"

    def test_duplicate_family_names_preserved(self):
        """Test that families with the same name at different paths are preserved.

        When two different parent families have children with the same name,
        the path-based keys ensure both are tracked correctly.

        Config structure:
        - family_A
          - shared_child  → key: 'family_A/shared_child'
        - family_B
          - shared_child  → key: 'family_B/shared_child'
        """
        flat_hierarchy = WorkflowSuite._extract_family_hierarchy(duplicate_name_config)

        # Both shared_child families are preserved with full paths
        assert 'family_A/shared_child' in flat_hierarchy
        assert 'family_B/shared_child' in flat_hierarchy
        # We expect 4 families total: family_A, family_B, and both shared_child
        assert len(flat_hierarchy) == 4, \
            f"Expected 4 families, got {len(flat_hierarchy)}: {flat_hierarchy}"

    def test_deploy_paths(self, tmp_path):
        """Test that tasks in anchor families get correct deploy paths.

        AnchorFamilies affect where .ecf files are deployed:
        - Tasks in anchor families: scripts/family_A/task_A1.ecf
        - Tasks in nested anchor families: scripts/family_A/family_Aa/task_Aa1.ecf
        """
        suite_dir = tmp_path / "testSuite"

        with WorkflowSuite('testSuite',
                           host=pf.LocalHost('localhost'),
                           files=str(suite_dir / 'scripts')):
            with pf.AnchorFamily('family_A'):
                t1 = pf.Task('task_A1', script='echo A1')
                with pf.AnchorFamily('family_Aa'):
                    t2 = pf.Task('task_Aa1', script='echo Aa1')

        scripts_dir = str(suite_dir / 'scripts')
        assert t1.deploy_path == f"{scripts_dir}/family_A/task_A1.ecf"
        assert t2.deploy_path == f"{scripts_dir}/family_A/family_Aa/task_Aa1.ecf"

    def test_executable_children(self):
        """Test that executable_children returns only tasks and families."""
        with WorkflowSuite('testSuite', host=pf.LocalHost('localhost')):
            with pf.AnchorFamily('family_A') as fam_A:
                pf.Variable('VAR1', 'value1')
                t1 = pf.Task('task_A1', script='echo A1')
                with pf.AnchorFamily('family_Aa') as fam_Aa:
                    t2 = pf.Task('task_Aa1', script='echo Aa1')
                t3 = pf.Task('task_A2', script='echo A2')

        children = fam_A.executable_children

        # Should include tasks and families, but NOT variables
        # Use 'is' for identity checks since pyflow objects override __eq__
        assert any(c is t1 for c in children)
        assert any(c is fam_Aa for c in children)
        assert any(c is t3 for c in children)
        assert not any(c is t2 for c in children)  # t2 is inside fam_Aa, not a direct child
        assert len(children) == 3

    def test_children_includes_all(self):
        """Test that children returns all direct children including variables."""
        with WorkflowSuite('testSuite', host=pf.LocalHost('localhost')):
            with pf.AnchorFamily('family_A') as fam_A:
                var1 = pf.Variable('VAR1', 'value1')
                t1 = pf.Task('task_A1', script='echo A1')
                with pf.AnchorFamily('family_Aa') as fam_Aa:
                    t2 = pf.Task('task_Aa1', script='echo Aa1')

        children = fam_A.children

        # Should include everything: variables, tasks, families
        # Use 'is' for identity checks since pyflow objects override __eq__
        assert any(c is var1 for c in children)
        assert any(c is t1 for c in children)
        assert any(c is fam_Aa for c in children)
        assert not any(c is t2 for c in children)  # t2 is inside fam_Aa, not a direct child
