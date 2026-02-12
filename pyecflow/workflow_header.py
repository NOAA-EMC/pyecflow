"""Workflow header module for pyecflow.

This module provides functionality to ensure header files (head.h, envir-p1.h,
tail.h) are present in the ecFlow suite's include/ directory. If they are not
found, they are copied from the package's static/ directory.
"""

import os

# Header files that should be present in the include/ directory
HEADER_FILES = ['head.h', 'envir-p1.h', 'tail.h']

# Path to the static/ directory relative to this file
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')


def read_static_file(filename: str) -> str:
    """Read the contents of a file from the package's static/ directory.

    Parameters
    ----------
    filename : str
        The name of the file to read.

    Returns
    -------
    str
        The contents of the file.

    Raises
    ------
    FileNotFoundError
        If the file does not exist in the static/ directory.
    """
    file_path = os.path.join(STATIC_DIR, filename)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(
            f"Header file '{filename}' not found in static/"
        )
    with open(file_path) as f:
        return f.read()


def ensure_headers(include_dir: str) -> list:
    """Ensure all required header files are present in the include directory.

    Checks if head.h, envir-p1.h, and tail.h exist in the specified include
    directory. Any missing files are copied from the package's static/
    directory.

    Parameters
    ----------
    include_dir : str
        The path to the suite's include/ directory.

    Returns
    -------
    list
        A list of filenames that were copied (empty if all files existed).

    Examples
    --------
    >>> copied = ensure_headers('/path/to/suite/include')
    >>> if copied:
    ...     print(f"Copied: {copied}")
    ... else:
    ...     print("All headers already present")
    """
    copied_files = []

    # Create include directory if it doesn't exist
    if not os.path.exists(include_dir):
        os.makedirs(include_dir, exist_ok=True)

    for header_file in HEADER_FILES:
        dest_path = os.path.join(include_dir, header_file)

        if not os.path.isfile(dest_path):
            content = read_static_file(header_file)
            with open(dest_path, 'w') as f:
                f.write(content)
            copied_files.append(header_file)

    return copied_files


def headers_exist(include_dir: str) -> bool:
    """Check if all required header files exist in the include directory.

    Parameters
    ----------
    include_dir : str
        The path to the suite's include/ directory.

    Returns
    -------
    bool
        True if all header files exist, False otherwise.
    """
    for header_file in HEADER_FILES:
        if not os.path.isfile(os.path.join(include_dir, header_file)):
            return False
    return True


def list_missing_headers(include_dir: str) -> list:
    """List header files that are missing from the include directory.

    Parameters
    ----------
    include_dir : str
        The path to the suite's include/ directory.

    Returns
    -------
    list
        List of missing header filenames.
    """
    missing = []
    for header_file in HEADER_FILES:
        if not os.path.isfile(os.path.join(include_dir, header_file)):
            missing.append(header_file)
    return missing
