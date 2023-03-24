# pyecFlow
An application to create ecFlow suite definition file and scripts

## Installation

### Dependencies
#### Required
* [Python](https://www.python.org) 3.7+
* [ecFlow](https://github.com/ecmwf/ecflow) 5.10.0
* [pyflow](https://github.com/ecmwf/pyflow) 3.1.0

### Install from source
Follow [ecFlow installation instructions](https://github.com/ecmwf/ecflow#install-from-source) and after all steps make sure to set following environment variable to correct paths.
```bash
export ECFLOW_DIR=/path/to/ecflow
git clone https://github.com/aerorahul/pyecFlow.git
cd pyecFlow
pip install .
```