"""Workflow suite module for pyecflow.

This module provides the WorkflowSuite class for creating
suites in ecFlow workflows.
"""

# imports
import os

import pyflow as pf

from .workflow_task import WorkflowTask


class WorkflowSuite(pf.Suite):
    """A workflow suite that extends pyflow's Suite.

    This class represents a suite in an ecFlow workflow. A suite is the top-level
    container in the ecFlow hierarchy and can contain families and tasks. Each
    suite is independent and can be loaded and run separately.
    """

    def generate_anchor_families(self, dict_fam_map):
        """Generate the anchor family structure under a suite.

        Creates a hierarchical structure of anchor families directly
        under the given suite and returns them for later use.

        Parameters
        ----------
        dict_fam_map : dict
            Dictionary mapping parent names to lists of child names.

        Returns
        -------
        dict
            Dictionary mapping parent names to the created AnchorFamily objects.

        Examples
        --------
        >>> config = {'family_X': ['family_X1', 'family_X2']}
        >>> dict_of_all_family_objs = suite.generate_anchor_families(config)
        >>> WorkflowSuite.generate_tasks(dict_of_all_family_objs, tasks_config)
        """
        created_parents = {}
        for parent_name, children in dict_fam_map.items():
            with self:  # check if self is ok, or better way
                parent = pf.AnchorFamily(parent_name)
            created_parents[parent_name] = parent
            for child_name in children:
                with parent:
                    child = pf.AnchorFamily(child_name)
                created_parents[child_name] = child
        return created_parents

    @staticmethod
    def generate_tasks(dict_of_all_family_objs, nested_dict_of_config):
        """Add tasks to the given anchor families.

        Creates WorkflowTask instances within each anchor family
        based on the task dictionary.

        Child families are processed before tasks at each level, ensuring
        that in the ecFlow definition, nested families appear before
        sibling tasks.

        Parameters
        ----------
        dict_of_all_family_objs : dict
            Dictionary mapping parent names to AnchorFamily objects.
        nested_dict_of_config : dict
            Dictionary mapping parent names to their task/children config.

        Examples
        --------
        >>> dict_of_all_family_objs = WorkflowSuite.generate_anchor_families(suite, families_config)
        >>> WorkflowSuite.generate_tasks(dict_of_all_family_objs, tasks_config)
        """
        for parent_name, parent_config in nested_dict_of_config.items():
            parent = dict_of_all_family_objs[parent_name]
            # Recurse into child families first
            children_config = parent_config.get('children', {})
            if children_config:
                WorkflowSuite.generate_tasks(dict_of_all_family_objs, children_config)
            # Add tasks to this family after children
            for task_name, task_context in parent_config.get('tasks', {}).items():
                with parent:
                    WorkflowTask(task_name, task_context)

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
        if not os.path.exists(include_dir):
            os.makedirs(include_dir, exist_ok=True)

        # TODO: This needs to be implemented by methods in header.py from pyflow
        # for header_file in self.headers:
        #    header_file_path = header_file.filepath
        #    if os.path.exists(header_file_path):
        #        shutil.copy(header_file_path, include_dir)

        # Create scripts directory and deploy scripts
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir, exist_ok=True)

        self.deploy_suite()
