"""Workflow suite module for pyecflow.

This module provides the WorkflowSuite class for creating
suites in ecFlow workflows.
"""

# imports
import os
import warnings

import pyflow as pf

from .workflow_include import ensure_includes
from .workflow_task import WorkflowTask


class WorkflowSuite(pf.Suite):
    """A workflow suite that extends pyflow's Suite.

    This class represents a suite in an ecFlow workflow. A suite is the top-level
    container in the ecFlow hierarchy and can contain families and tasks. Each
    suite is independent and can be loaded and run separately.

    Attributes
    ----------
    _include_paths : dict
        Dictionary storing custom include file paths extracted from config.
        Keys are 'head', 'tail', 'envir'. Values are file paths or None.
    """

    def __init__(self, *args, **kwargs):
        """Initialize WorkflowSuite with include path storage."""
        super().__init__(*args, **kwargs)
        # Initialize include paths - will be populated by generate_tree()
        self._include_paths = {
            'head': None,
            'tail': None,
            'envir': None
        }

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
            - Keys are family names (str) or 'includes' for include config
            - Values are dicts with optional keys:
                - 'children': dict[str, dict] - nested child families
                - 'tasks': dict[str, dict] - task configurations

            Input structure::

                {
                    'includes': {                        # optional
                        'head': '/path/to/head.h',       # optional
                        'tail': '/path/to/tail.h',       # optional
                        'envir': '/path/to/envir-p1.h'   # optional
                    },
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
        ...     'includes': {'head': '/custom/head.h'},  # optional
        ...     'family_A': {
        ...         'tasks': {'task1': {'variables': {...}, 'script': '...'}},
        ...         'children': {'family_Aa': {'tasks': {...}}}
        ...     }
        ... }
        >>> dict_of_all_family_objs = suite.generate_tree(config)
        """
        # Extract include configuration if present (use get to avoid mutating caller's dict)
        includes_config = nested_config.get('includes', None)
        if includes_config:
            self._include_paths['head'] = includes_config.get('head') or None
            self._include_paths['tail'] = includes_config.get('tail') or None
            self._include_paths['envir'] = includes_config.get('envir') or None

        # Set WorkflowTask class attribute for envir-p1.h inclusion
        # Only include if envir path is explicitly configured (opt-in)
        WorkflowTask._include_envir = self._include_paths.get('envir') is not None

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
                # Skip reserved keys that aren't family names
                if family_name == 'includes':
                    continue
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

    def generate_suite(self, suite_dir: str = './',
                       head_path: str = None,
                       tail_path: str = None,
                       envir_path: str = None):
        """Generate an ecFlow suite definition file and deploy associated files.

        This method generates the necessary files and directory structure for
        an ecFlow suite. The suite directory is organized with subdirectories
        for definitions, include files, and scripts.

        Parameters
        ----------
        suite_dir : str, optional
            The base directory where the suite files will be deployed.
            Default is './'.
        head_path : str, optional
            Path to a custom head.h file. Overrides config and defaults.
        tail_path : str, optional
            Path to a custom tail.h file. Overrides config and defaults.
        envir_path : str, optional
            Path to a custom envir-p1.h file. Overrides config and defaults.

        Returns
        -------
        None
            Files are created as side effects in the specified suite_dir.

        Notes
        -----
        The suite directory structure created is as follows:

        - def/ : Contains the suite definition file and validates the suite
        - include/ : Contains include files (head.h, tail.h, envir-p1.h)
        - scripts/ : Contains ecf script files, organized by families as
          subdirectories if applicable

        **Include File Customization**

        There are three ways to customize include files, in order of precedence:

        1. **Method parameters** (highest priority): Pass ``head_path``,
           ``tail_path``, or ``envir_path`` directly to this method.
        2. **Config section**: Include an ``'includes'`` section in the config
           passed to ``generate_tree()``.
        3. **Package defaults** (lowest priority): If no custom paths are
           specified, default files from the package's ``static/`` directory
           are used.

        The method performs the following operations:

        1. Creates the suite directory if it doesn't exist
        2. Creates subdirectories for def, include, and scripts
        3. Validates the suite definition with check_definition()
        4. Deploys suite scripts using deploy_suite()
        5. Copies include files to include/ (custom or default)

        Examples
        --------
        >>> suite = WorkflowSuite('my_suite')
        >>> suite.generate_suite(suite_dir='/path/to/suite')

        With method parameter overrides:

        >>> suite.generate_suite(
        ...     suite_dir='/path/to/suite',
        ...     head_path='/custom/head.h',
        ...     tail_path='/custom/tail.h'
        ... )

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

        # Create include directory - pyflow will deploy header files here
        if not os.path.exists(include_dir):
            os.makedirs(include_dir, exist_ok=True)
        # Set ECF_INCLUDE so pyflow knows where to deploy header files
        self.ECF_INCLUDE = include_dir

        # Create scripts directory and deploy scripts
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir, exist_ok=True)

        # Determine effective envir path (method param overrides config)
        effective_envir_path = envir_path or self._include_paths.get('envir', None)

        # Update WorkflowTask class attribute for envir inclusion before deploying scripts
        # This handles the case where envir_path is passed to generate_suite()
        WorkflowTask._include_envir = effective_envir_path is not None

        # Deploy scripts
        self.deploy_suite()

        # Copy includes (head.h, tail.h required; envir-p1.h only if configured)
        # Priority: method parameters > config values > package defaults
        ensure_includes(
            include_dir,
            head_path=head_path or self._include_paths.get('head', None),
            tail_path=tail_path or self._include_paths.get('tail', None),
            envir_path=effective_envir_path
        )
