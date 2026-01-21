# pyecflow
An application to create `ecFlow` suites

## Installation

### Dependencies
#### Required
* [Python](https://www.python.org) 3.11+
* [ecFlow](https://github.com/ecmwf/ecflow)
* [pyflow](https://github.com/ecmwf/pyflow)

### Install using conda
The recommended way to install `pyecFlow` is using conda. This will also install `ecFlow`.
```bash
conda env create -n pyecflow -f environment.yml
conda activate pyecflow
conda install --file test-environment.txt  # optional for running pyecflow tests
pip install .  # install pyecflow
```

### Install using pip
Installing with pip requires that you have already installed `ecFlow`.
To install `ecFlow`, follow [ecFlow installation instructions](https://ecflow.readthedocs.io/en/latest/install/index.html). After all steps make sure to set following environment variable to correct paths.
```bash
export ECFLOW_DIR=/path/to/ecflow
pip install .'[test]'  # optional [test] for running tests
```

### Testing
You can run the tests using the following command:
```bash
pytest tests/
```
