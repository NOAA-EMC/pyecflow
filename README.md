# pyecflow
An application to create `ecFlow` suites

## Overview

`pyecflow` provides a Python interface for creating and managing ecFlow workflows with the following main components:

* **WorkflowSuite**: Top-level container for ecFlow workflows with methods to generate suite directory structure and deploy files
* **WorkflowAnchorFamily**: Anchor family for organizing workflow hierarchy and script file organization
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
import pyflow as pf
from pyecflow import WorkflowSuite

# Define workflow structure as a nested config dictionary
config = {
    'family_A': {
        'tasks': {
            'task_A1': {
                'variables': {'VAR1': 'value1'},
                'script': 'echo task_A1 VAR1=$VAR1',
            },
        },
        'children': {
            'family_Aa': {
                'tasks': {
                    'task_Aa1': {
                        'variables': {'VAR1': 'value2'},
                        'script': 'echo task_Aa1 VAR1=$VAR1',
                    },
                },
            },
        },
    },
}

# Create a suite
suite = WorkflowSuite(
    'my_suite',
    host=pf.LocalHost('localhost'),
    files='/path/to/suite/scripts'
)

# Generate family hierarchy and tasks from config
suite.generate_tree(config)

# Generate suite directory structure and deploy files
suite.generate_suite(suite_dir='/path/to/suite')
```

### Custom Header Files

By default, `pyecflow` uses standard header files (`head.h`, `tail.h`, `envir-p1.h`) from the package's `static/` directory. You can specify custom header files in your configuration:

```python
config = {
    # Optional: specify custom header file paths
    'headers': {
        'head': '/path/to/custom/head.h',    # or omit for default
        'tail': '/path/to/custom/tail.h',    # or omit for default
        'envir': '/path/to/custom/envir-p1.h'  # or omit for default
    },
    'family_A': {
        'tasks': {
            'task_A1': {
                'variables': {'VAR1': 'value1'},
                'script': 'echo task_A1',
            },
        },
    },
}
```

If you omit the `headers` section entirely, or leave any path empty/null, the default headers from the package will be used.

For more examples, see the notebooks in the `notebooks/` directory.
