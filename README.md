# pyecflow
An application to create `ecFlow` suites

## Overview

`pyecflow` provides a Python interface for creating and managing ecFlow workflows with the following main components:

* **WorkflowSuite**: Top-level container for ecFlow workflows with methods to generate suite directory structure and deploy files
* **WorkflowFamily**: Container for organizing and grouping related tasks in a workflow hierarchy
* **WorkflowAnchorFamily**: Special family type for synchronizing tasks across different parts of the workflow
* **WorkflowTask**: Individual task representing a single job or script to be executed

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

## Usage

### Basic Example

```python
from pyecflow import WorkflowSuite, WorkflowFamily, WorkflowTask

# Create a suite
suite = WorkflowSuite('my_suite')

# Create a family
family = WorkflowFamily('my_family')

# Create a task
task_context = {
    'variables': {'VAR1': 'value1'},
    'script': '/path/to/script.sh'
}
task = WorkflowTask('my_task', context=task_context)

# Add task to family
family.add(task)

# Add family to suite
suite.add(family)

# Generate suite directory structure
suite.generate_suite(suite_dir='/path/to/suite')
```

For more examples, see the notebooks in the `notebooks/` directory.
