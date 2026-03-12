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

### Custom Include Files

By default, `pyecflow` uses standard include files (`head.h`, `tail.h`, `envir-p1.h`) from the package's `static/` directory. There are three ways to customize these files, in order of precedence:

#### 1. Method Parameters (Highest Priority)

Pass paths directly to `generate_suite()`:

```python
suite.generate_suite(
    suite_dir='/path/to/suite',
    head_path='/custom/head.h',
    tail_path='/custom/tail.h',
    envir_path='/custom/envir-p1.h'
)
```

#### 2. Config Section

Include an `'includes'` section in your configuration:

```python
config = {
    'includes': {
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

#### 3. Package Defaults (Lowest Priority)

If you omit the `includes` section entirely, or leave any path empty/null, the default includes from the package's `static/` directory will be used.

### Generated .ecf File Format

The generated `.ecf` files use the traditional ecFlow `%include` directive approach:

```bash
#!/bin/bash

%include <head.h>
%include <envir-p1.h>

%nopp

# Your script content here
echo "Hello World"

%end

%include <tail.h>

%manual
Optional manual/help text for the task.
%end
```

**How it works:**
1. Include files (`head.h`, `envir-p1.h`, `tail.h`) are deployed to `suite/include/`
2. The `.ecf` files contain `%include` directives that reference these files by name
3. At runtime, ecFlow's pre-processor expands the `%include` directives by reading from the `ECF_INCLUDE` directory

This approach allows you to:
- Maintain a single source of truth for headers/footers
- Easily swap include files without regenerating `.ecf` files
- Follow standard ecFlow patterns that operations teams expect
