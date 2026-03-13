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

`pyecflow` manages include files for ecFlow suites:

- **`head.h`** (required): ecFlow job initialization - sets ECF_* variables and calls `ecflow_client --init`
- **`tail.h`** (required): ecFlow job completion - calls `ecflow_client --complete`
- **`envir-p1.h`** (optional): NCO environment extension - only deployed/included when explicitly configured

By default, `head.h` and `tail.h` are copied from the package's `static/` directory. The optional `envir-p1.h` is only included when you provide a path to it.

#### Customizing Include Files

There are three ways to customize include files, in order of precedence:

**1. Method Parameters (Highest Priority)**

Pass paths directly to `generate_suite()`:

```python
suite.generate_suite(
    suite_dir='/path/to/suite',
    head_path='/custom/head.h',
    tail_path='/custom/tail.h',
    envir_path='/custom/envir-p1.h'  # optional NCO extension
)
```

**2. Config Section**

Include an `'includes'` section in your configuration:

```python
config = {
    'includes': {
        'head': '/path/to/custom/head.h',    # or omit for default
        'tail': '/path/to/custom/tail.h',    # or omit for default
        'envir': '/path/to/custom/envir-p1.h'  # optional, only include if needed
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

**3. Package Defaults (Lowest Priority)**

If you omit the `includes` section entirely, or leave paths empty/null, the default `head.h` and `tail.h` from the package's `static/` directory will be used. The `envir-p1.h` will only be included if explicitly configured.

**Using the Package's Default envir-p1.h**

To use the NCO environment extension with the package's built-in `envir-p1.h`:

```python
from pyecflow.workflow_include import STATIC_DIR
import os

config = {
    'includes': {
        'envir': os.path.join(STATIC_DIR, 'envir-p1.h')
    },
    'family_A': { ... }
}
```

### Generated .ecf File Format

The generated `.ecf` files use the traditional ecFlow `%include` directive approach:

```bash
#!/bin/bash

%include <head.h>

%nopp

# Your script content here
echo "Hello World"

%end

%include <tail.h>
```

If `envir-p1.h` is configured (via `includes.envir`), it's included after `head.h`:

```bash
%include <head.h>
%include <envir-p1.h>

%nopp
...
```

If the task has manual content (via the `manual` key in config), a `%manual` section is appended:

```bash
%manual
Help text for the task.
%end
```

**How it works:**
1. Required include files (`head.h`, `tail.h`) are deployed to `suite/include/`
2. Optional `envir-p1.h` is deployed only when configured
3. The `.ecf` files contain `%include` directives that reference these files by name
4. At runtime, ecFlow's pre-processor expands the `%include` directives by reading from the `ECF_INCLUDE` directory

This approach allows you to:
- Maintain a single source of truth for headers/footers
- Easily swap include files without regenerating `.ecf` files
- Follow standard ecFlow patterns that operations teams expect
