"""Workflow anchor family module for pyecflow.

This module provides the WorkflowAnchorFamily class for creating
anchor families in ecFlow workflows.
"""

import pyflow as pf


class WorkflowAnchorFamily(pf.AnchorFamily):
    """A workflow anchor family that extends pyflow's AnchorFamily.

    This class represents an anchor family in an ecFlow workflow, which can
    contain nested families and tasks. An anchor family is a special type of
    family that provides script file organization and can be used to
    synchronize tasks across different parts of the workflow.

    This class primarily provides static methods for generating anchor family
    hierarchies. Use generate_anchor_families() to create a family structure
    under a suite or parent family.

    Class Attributes
    ----------------
    DEFAULT_FAMILIES : dict
        Default family structure for testing/development. Maps top-level
        family names to lists of child family names.

    See Also
    --------
    WorkflowTask.generate_tasks : Populates anchor families with tasks.
    WorkflowSuite.add_anchor_family : Convenience method to add families to a suite.
    """

    # Commented out for future reference:
    # def __init__(self, name: str, famA_tasks: dict = None, **kwargs):
    #     super().__init__(name)
    #     task_triggers = {}
    #
    #     # If famA_tasks is provided, create tasks from the dictionary
    #     if famA_tasks is not None:
    #         for tt in famA_tasks.keys():
    #             task_tc = famA_tasks[tt]
    #             task = WorkflowTask(tt, task_tc)
    #             task_triggers[tt] = task
    #             self.add(task)
    #
    #     self.task_triggers = task_triggers

    # Default family structure for testing/development
    DEFAULT_FAMILIES = {
        'family_A': ['family_Aa', 'family_Ab'],
        'family_B': ['family_Ba'],
    }

    @staticmethod
    def generate_anchor_families(parent, families=None):
        """Generate the anchor family structure under a parent node.

        Creates a hierarchical structure of anchor families directly
        under the given parent.

        Parameters
        ----------
        parent : pf.Suite or pf.AnchorFamily
            The parent node to add anchor families to.
        families : dict, optional
            Dictionary mapping family names to lists of child family names.
            If None, uses DEFAULT_FAMILIES.

        Examples
        --------
        >>> # Using default structure
        >>> WorkflowAnchorFamily.generate_anchor_families(suite)

        >>> # Using custom structure from config
        >>> config = {'family_X': ['family_X1', 'family_X2']}
        >>> WorkflowAnchorFamily.generate_anchor_families(suite, config)
        """
        if families is None:
            families = WorkflowAnchorFamily.DEFAULT_FAMILIES

        for fam_name, children in families.items():
            with parent:
                fam = pf.AnchorFamily(fam_name)
            for child_name in children:
                with fam:
                    pf.AnchorFamily(child_name)
