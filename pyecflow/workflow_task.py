"""Workflow task module for pyecflow.

This module provides the WorkflowTask class for creating tasks in ecFlow
workflows using pyflow's tightly coupled header model.

The header content (head/tail) is defined as class attributes, ensuring
the %include directives and the deployed .h files come from the same
source of truth. This enables dynamic suite generation that can be
applied to any model.

Classes
-------
WorkflowTask
    A workflow task with ecFlow-compatible head and tail headers.
"""

# imports
import pyflow as pf


class WorkflowTask(pf.Task):
    # Docstring intentionally omitted to prevent pyflow from using it as %manual.
    # See module docstring for class documentation.
    #
    # Headers are defined as class attributes and pyflow automatically:
    # 1. Generates %include <workflowtask_head.h> directives in the .ecf script
    # 2. Deploys workflowtask_head.h and workflowtask_tail.h to include/
    #
    # Parameters:
    #   name : str - The name of the task.
    #   context : dict - Task configuration with 'variables', 'script', optional 'manual', 'envir'.
    #   **kwargs - Additional keyword arguments to pass to the parent Task class.

    # Head header - ecFlow initialization and job setup
    # pyflow generates: %include <workflowtask_head.h>
    head = """
# workflowtask_head.h - ecFlow task initialization

date
hostname
set -xe  # print commands as they are executed and enable signal trapping

export PS4='+ $SECONDS + '

if [[ -n "${PBS_JOBID}" ]]; then
  export job=${job:-${PBS_JOBNAME}}
  export jobid=${jobid:-${job}.${PBS_JOBID}}
elif [[ -n "${SLURM_JOB_ID}" ]]; then
  export job=${job:-${SLURM_JOB_NAME}}
  export jobid=${jobid:-${job}.${SLURM_JOB_ID}}
else
  export job=${job:-"demojob"}
  export jobid=${jobid:-${job}.$$}
fi

# Variables needed for communication with ecFlow
export ECF_NAME=%ECF_NAME%
export ECF_HOST=%ECF_LOGHOST%
export ECF_PORT=%ECF_PORT%
export ECF_PASS=%ECF_PASS%
export ECF_TRYNO=%ECF_TRYNO%
export ECF_RID=${ECF_RID:-${jobid}}
export ECF_JOB=%ECF_JOB%
export ECF_JOBOUT=%ECF_JOBOUT%

timeout 300 ecflow_client --init=${ECF_RID}
"""

    # Tail header - ecFlow completion notification
    # pyflow generates: %include <workflowtask_tail.h>
    tail = """
# workflowtask_tail.h - ecFlow task completion

timeout 300 ecflow_client --complete  # Notify ecFlow of a normal end
trap 0                    # Remove all traps
exit 0                    # End the shell
"""

    def __init__(self, name: str, context: dict, **kwargs):
        # Get script content, prepending any environment setup
        script = context.get('script', '')
        envir = context.get('envir', '')
        if envir:
            script = f"{envir}\n\n{script}"

        # Get manual from context, default to empty string to suppress class docstring
        manual = context.get('manual', '')

        super().__init__(
            name,
            variables=context.get('variables', {}),
            script=script,
            manual=manual,
            **kwargs,
        )
