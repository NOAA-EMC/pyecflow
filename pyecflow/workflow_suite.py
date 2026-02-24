"""Workflow suite module for pyecflow.

This module provides the WorkflowSuite class for creating
suites in ecFlow workflows.
"""

# imports
import os
import warnings

import pyflow as pf

from .workflow_header import ensure_headers
from .workflow_task import WorkflowTask


class WorkflowSuite(pf.Suite):
    """A workflow suite that extends pyflow's Suite.

    This class represents a suite in an ecFlow workflow. A suite is the top-level
    container in the ecFlow hierarchy and can contain families and tasks. Each
    suite is independent and can be loaded and run separately.
    """

    @staticmethod
    def _extract_family_hierarchy(nested_config, parent_path=''):
        """Recursively extract a flat family hierarchy from nested config.

        Converts a nested configuration dictionary into a flat mapping
        of family paths to their direct child family names. Uses full
        paths as keys to handle families with the same name at different
        locations in the hierarchy.

        Parameters
        ----------
        nested_config : dict[str, dict]
            Nested dictionary where:
            - Keys are family names (str)
            - Values are dicts with optional keys:
                - 'children': dict[str, dict] - nested child families
                - 'tasks': dict[str, dict] - task configurations

            Input structure::

                {
                    'family_name': {
                        'children': {<nested_config>},  # optional
                        'tasks': {...}                   # optional
                    },
                    ...
                }

        parent_path : str, optional
            The path to the parent family (used for recursion).
            Default is '' (root level).

        Returns
        -------
        dict[str, list[str]]
            Flat dictionary where:
            - Keys are full family paths (str), e.g., 'family_A/family_Aa'
            - Values are lists of direct child family names (list[str])

            Output structure::

                {
                    'family_A': ['family_Aa', 'family_Ab'],
                    'family_A/family_Aa': [],
                    'family_A/family_Ab': [],
                }

        Examples
        --------
        >>> config = {
        ...     'family_A': {
        ...         'children': {'family_Aa': {}, 'family_Ab': {}},
        ...         'tasks': {}
        ...     }
        ... }
        >>> WorkflowSuite._extract_family_hierarchy(config)
        {'family_A': ['family_Aa', 'family_Ab'], 'family_A/family_Aa': [], 'family_A/family_Ab': []}
        """
        result = {}
        for family_name, family_config in nested_config.items():
            # Skip empty family names
            if not family_name:
                warnings.warn("family name is empty, skipping")
                continue
            # Build full path for this family
            family_path = f"{parent_path}/{family_name}" if parent_path else family_name
            children_config = family_config.get('children', {}) if family_config else {}
            # Filter out empty child names
            valid_children = [name for name in children_config.keys() if name]
            if len(valid_children) < len(children_config):
                warnings.warn("family name is empty, skipping")
            result[family_path] = valid_children
            # Recursively process children with updated path
            if children_config:
                result.update(WorkflowSuite._extract_family_hierarchy(
                    children_config, parent_path=family_path
                ))
        return result

    def generate_tree(self, nested_config):
        """Generate the complete family and task tree under a suite.

        Creates a hierarchical structure of anchor families and their tasks
        directly under the suite. The nested_config dictionary is the source
        of truth for the workflow structure. Child families are created before
        tasks at each level, ensuring that in the ecFlow definition, nested
        families appear before sibling tasks.

        Parameters
        ----------
        nested_config : dict[str, dict]
            Nested dictionary where:
            - Keys are family names (str)
            - Values are dicts with optional keys:
                - 'children': dict[str, dict] - nested child families
                - 'tasks': dict[str, dict] - task configurations

            Input structure::

                {
                    'family_name': {
                        'children': {<nested_config>},  # optional
                        'tasks': {                       # optional
                            'task_name': {
                                'variables': {...},
                                'script': '...'
                            }
                        }
                    },
                    ...
                }

        Returns
        -------
        dict[str, pf.AnchorFamily]
            Dictionary where:
            - Keys are full family paths (str), e.g., 'family_A/family_Aa'
            - Values are the created pyflow AnchorFamily objects

            Output structure::

                {
                    'family_A': <AnchorFamily object>,
                    'family_A/family_Aa': <AnchorFamily object>,
                    ...
                }

        Examples
        --------
        >>> config = {
        ...     'family_A': {
        ...         'tasks': {'task1': {'variables': {...}, 'script': '...'}},
        ...         'children': {'family_Aa': {'tasks': {...}}}
        ...     }
        ... }
        >>> dict_of_all_family_objs = suite.generate_tree(config)
        """
        created_families = {}

        def _create_tree_recursive(parent_node, config_dict, parent_path=''):
            """Recursively create families and tasks under a parent node.

            This inner function walks the nested config, creating AnchorFamily
            objects under each parent using pyflow's context manager pattern.
            Child families are created before tasks to ensure proper ordering
            in the ecFlow definition.

            Parameters
            ----------
            parent_node : pf.Suite or pf.AnchorFamily
                The parent node to create children under.
            config_dict : dict
                The config dictionary at this level of nesting.
            parent_path : str
                The path to the parent family (used for building full paths).

            Side Effects
            ------------
            Populates the enclosing `created_families` dict with all
            created AnchorFamily objects keyed by full path.
            """
            for family_name, family_config in config_dict.items():
                # Skip empty family names
                if not family_name:
                    warnings.warn("family name is empty, skipping")
                    continue
                # Handle None family_config
                if family_config is None:
                    family_config = {}
                # Build full path for this family
                family_path = f"{parent_path}/{family_name}" if parent_path else family_name

                # Create the anchor family
                with parent_node:
                    family = pf.AnchorFamily(family_name)
                created_families[family_path] = family

                # Recursively create child families first
                children_config = family_config.get('children', {})
                if children_config:
                    _create_tree_recursive(family, children_config, parent_path=family_path)

                # Add tasks to this family after children
                for task_name, task_context in family_config.get('tasks', {}).items():
                    # Skip empty task names
                    if not task_name:
                        warnings.warn("task name is empty, skipping")
                        continue
                    # Handle None task_context
                    if task_context is None:
                        task_context = {}
                    # Validate and filter variables
                    variables = task_context.get('variables', {})
                    if variables:
                        filtered_vars = {}
                        for var_name, var_value in variables.items():
                            if not var_name:
                                warnings.warn("variable name is empty, skipping")
                                continue
                            filtered_vars[var_name] = var_value
                        task_context = {**task_context, 'variables': filtered_vars}
                    # Validate script
                    script = task_context.get('script', '')
                    if not script:
                        warnings.warn("script is empty, skipping task")
                        continue
                    with family:
                        WorkflowTask(task_name, task_context)

        _create_tree_recursive(self, nested_config)
        return created_families

    def generate_suite(self, suite_dir: str = './'):
        """Generate an ecFlow suite definition file and deploy associated files.

        This method generates the necessary files and directory structure for
        an ecFlow suite. The suite directory is organized with subdirectories
        for definitions, include files, and scripts.

        Parameters
        ----------
        suite_dir : str, optional
            The base directory where the suite files will be deployed.
            Default is './'.

        Returns
        -------
        None
            Files are created as side effects in the specified suite_dir.

        Notes
        -----
        The suite directory structure created is as follows:

        - def/ : Contains the suite definition file and validates the suite
        - include/ : Contains any include files (header files)
        - scripts/ : Contains ecf script files, organized by families as
          subdirectories if applicable

        The method performs the following operations:

        1. Creates the suite directory if it doesn't exist
        2. Creates subdirectories for def, include, and scripts
        3. Validates the suite definition with check_definition()
        4. Deploys suite scripts using deploy_suite()

        Examples
        --------
        >>> suite = WorkflowSuite('my_suite')
        >>> suite.generate_suite(suite_dir='/path/to/suite')

        This will create the following structure:
        /path/to/suite/
            def/
            include/
            scripts/
        """
        # Ensure the suite directory exists
        if not os.path.exists(suite_dir):
            os.makedirs(suite_dir, exist_ok=True)

        # Define directory paths
        scripts_dir = os.path.join(suite_dir, 'scripts')
        include_dir = os.path.join(suite_dir, 'include')
        def_dir = os.path.join(suite_dir, 'def')

        # Create def directory
        if not os.path.exists(def_dir):
            os.makedirs(def_dir, exist_ok=True)

        # Save the suite definition file
        self.check_definition()
        suite_def = self.ecflow_definition()
        suite_def.save_as_defs(os.path.join(def_dir, f'{self.name}.def'))

        # Create include directory and copy header files
        ensure_headers(include_dir)

        # Create scripts directory and deploy scripts
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir, exist_ok=True)

        self.deploy_suite()
