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

    Parameters
    ----------
    name : str
        The name of the suite.
    *args
        Variable length argument list to pass to the parent Suite class.
    **kwargs
        Arbitrary keyword arguments to pass to the parent Suite class.
    """

    def __init__(self, name: str, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
    # don't need this method
    # def add_anchor_family(self, families):
        """Add anchor families directly to the suite.

        This method generates an anchor family hierarchy directly under the suite
        and returns the created families for later use.

        Parameters
        ----------
        families : dict
            Dictionary mapping family names to lists of child family names.

        Returns
        -------
        dict
            Dictionary mapping family names to the created AnchorFamily objects.

        Examples
        --------
        >>> config = {'family_X': ['family_X1', 'family_X2']}
        >>> families = suite.add_anchor_family(config)
        >>> WorkflowSuite.generate_tasks(families, tasks_config)
        """
        # return self.generate_anchor_families(families)

    def generate_anchor_families(self, families):
        """Generate the anchor family structure under a suite.

        Creates a hierarchical structure of anchor families directly
        under the given suite and returns them for later use.

        Parameters
        ----------
        suite : pf.Suite
            The suite to add anchor families to.
        families : dict
            Dictionary mapping family names to lists of child family names.

        Returns
        -------
        dict
            Dictionary mapping family names to the created AnchorFamily objects.

        Examples
        --------
        >>> config = {'family_X': ['family_X1', 'family_X2']}
        >>> families = WorkflowSuite.generate_anchor_families(suite, config)
        >>> WorkflowSuite.generate_tasks(families, tasks_config)
        """
        created_families = {}
        for fam_name, children in families.items():
            with self:  # check if self is ok, or better way
                fam = pf.AnchorFamily(fam_name)
            created_families[fam_name] = fam
            for child_name in children:
                with fam:
                    child_fam = pf.AnchorFamily(child_name)
                created_families[child_name] = child_fam
        return created_families

    @staticmethod
    def generate_tasks(families, tasks):
        """Add tasks to the given anchor families.

        Creates WorkflowTask instances within each anchor family
        based on the task dictionary.

        Child families are processed before tasks at each level, ensuring
        that in the ecFlow definition, nested families appear before
        sibling tasks.

        Parameters
        ----------
        families : dict
            Dictionary mapping family names to AnchorFamily objects.
        tasks : dict
            Dictionary mapping family names to their task/children config.

        Examples
        --------
        >>> families = WorkflowSuite.generate_anchor_families(suite, families_config)
        >>> WorkflowSuite.generate_tasks(families, tasks_config)
        """
        for fam_name, fam_config in tasks.items():
            fam = families[fam_name]
            # Recurse into child families first
            children_config = fam_config.get('children', {})
            if children_config:
                WorkflowSuite.generate_tasks(families, children_config)
            # Add tasks to this family after children
            for task_name, task_context in fam_config.get('tasks', {}).items():
                with fam:
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
