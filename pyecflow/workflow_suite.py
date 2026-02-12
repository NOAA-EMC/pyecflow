"""Workflow suite module for pyecflow.

This module provides the WorkflowSuite class for creating
suites in ecFlow workflows.
"""

# imports
import os

import pyflow as pf

from .workflow_anchorfamily import WorkflowAnchorFamily
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

    def add_anchor_family(self, families):
        """Add anchor families directly to the suite.

        This method generates an anchor family hierarchy directly under the suite.

        Parameters
        ----------
        families : dict
            Dictionary mapping family names to lists of child family names.

        Examples
        --------
        >>> # Using custom structure from config
        >>> config = {'family_X': ['family_X1', 'family_X2']}
        >>> suite.add_anchor_family(config)
        """
        WorkflowSuite.generate_anchor_families(self, families)

    @staticmethod
    def generate_anchor_families(parent, families):
        """Generate the anchor family structure under a parent node.

        Creates a hierarchical structure of anchor families directly
        under the given parent.

        Parameters
        ----------
        parent : pf.Suite or pf.AnchorFamily
            The parent node to add anchor families to.
        families : dict
            Dictionary mapping family names to lists of child family names.

        Examples
        --------
        >>> # Using custom structure from config
        >>> config = {'family_X': ['family_X1', 'family_X2']}
        >>> WorkflowSuite.generate_anchor_families(suite, config)
        """
        for fam_name, children in families.items():
            with parent:
                fam = pf.AnchorFamily(fam_name)
            for child_name in children:
                with fam:
                    pf.AnchorFamily(child_name)

    @staticmethod
    def generate_tasks(suite, tasks):
        """Add tasks to the anchor families in the suite.

        Creates WorkflowTask instances within each anchor family
        based on the task dictionary. The anchor families must already
        exist on the suite before calling this method.

        Child families are processed before tasks at each level, ensuring
        that in the ecFlow definition, nested families appear before
        sibling tasks.

        Parameters
        ----------
        suite : pf.Suite
            The suite containing the anchor families to add tasks to.
        tasks : dict
            Dictionary mapping family names to their task/children config.

        Examples
        --------
        >>> # Using custom structure from config
        >>> config = load_yaml('tasks.yml')
        >>> WorkflowSuite.generate_tasks(suite, config)
        """
        WorkflowSuite._add_tasks_to_families(suite, tasks)

    @staticmethod
    def _add_tasks_to_families(parent, family_tasks):
        """Recursively add tasks to existing anchor families.

        Processes child families before adding tasks at each level to ensure
        proper ordering in the ecFlow definition (children appear before
        sibling tasks).

        Parameters
        ----------
        parent : pf.Suite or pf.AnchorFamily
            The parent node containing the families.
        family_tasks : dict
            Dictionary mapping family names to their task/children config.
        """
        for fam_name, fam_config in family_tasks.items():
            fam = getattr(parent, fam_name)
            # Recurse into child families first
            children = fam_config.get('children', {})
            if children:
                WorkflowSuite._add_tasks_to_families(fam, children)
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
