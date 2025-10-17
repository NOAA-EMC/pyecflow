# head.h

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
