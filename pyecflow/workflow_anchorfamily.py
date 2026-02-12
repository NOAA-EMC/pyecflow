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

    Parameters
    ----------
    name : str
        The name of the anchor family.
    context : dict, optional
        A dictionary containing family configuration with optional keys:
        - 'children' : list
            Names of child families to create under this family.
    **kwargs
        Additional keyword arguments to pass to the parent AnchorFamily class.

    See Also
    --------
    WorkflowSuite.generate_anchor_families : Creates anchor family hierarchies under a suite.
    WorkflowSuite.generate_tasks : Populates anchor families with tasks.
    WorkflowSuite.add_anchor_family : Convenience method to add families to a suite.
    """

    def __init__(self, name: str, context: dict = None, **kwargs):
        """Initialize a WorkflowAnchorFamily.

        Parameters
        ----------
        name : str
            The name of the anchor family.
        context : dict, optional
            A dictionary containing family configuration with optional keys:
            - 'children' : list
                Names of child families to create under this family.
        **kwargs
            Additional keyword arguments to pass to the parent AnchorFamily class.
        """
        super().__init__(name, **kwargs)
        if context is not None:
            children = context.get('children', [])
            for child_name in children:
                with self:
                    pf.AnchorFamily(child_name)
