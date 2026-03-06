"""Workflow header module for pyecflow.

This module provides functions to manage header files (head.h, envir-p1.h,
tail.h) for ecFlow suites. Users can either provide custom paths to these
files or use the default files from the package's static/ directory.

Functions
---------
ensure_headers
    Ensure all required header files are present in the include directory.
headers_exist
    Check if all required header files exist in the include directory.
list_missing_headers
    List header files that are missing from the include directory.
read_static_file
    Read the contents of a file from the package's static/ directory.
"""

import os
from abc import ABC, abstractmethod

# Header files that should be present in the include/ directory
HEADER_FILES = ['head.h', 'envir-p1.h', 'tail.h']

# Path to the static/ directory relative to this file
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')

# Default header file names
DEFAULT_HEAD = 'head.h'
DEFAULT_TAIL = 'tail.h'
DEFAULT_ENVIR = 'envir-p1.h'


class _Header(ABC):
    """Abstract base class for header file management (internal use)."""

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        """str: The name of the header file."""
        return self._name

    @abstractmethod
    def get_content(self) -> str:
        """Get the content of the header file.

        Returns
        -------
        str
            The content of the header file.
        """
        pass

    def install(self, include_dir: str) -> str:
        """Install the header file to the include directory.

        Parameters
        ----------
        include_dir : str
            The path to the suite's include/ directory.

        Returns
        -------
        str
            The path to the installed header file.
        """
        if not os.path.exists(include_dir):
            os.makedirs(include_dir, exist_ok=True)

        dest_path = os.path.join(include_dir, self._name)
        content = self.get_content()
        with open(dest_path, 'w') as f:
            f.write(content)
        return dest_path


class _FileHeader(_Header):
    """Header that reads content from a user-specified file path (internal use)."""

    def __init__(self, name: str, path: str):
        super().__init__(name)
        self._path = path

    @property
    def path(self) -> str:
        """str: The path to the source file."""
        return self._path

    def get_content(self) -> str:
        """Read and return the content from the source file.

        Returns
        -------
        str
            The content of the source file.

        Raises
        ------
        FileNotFoundError
            If the source file does not exist.
        """
        if not os.path.isfile(self._path):
            raise FileNotFoundError(
                f"Header source file '{self._path}' not found"
            )
        with open(self._path) as f:
            return f.read()


class _StaticHeader(_Header):
    """Header that uses the default file from the package's static/ directory (internal use)."""

    def get_content(self) -> str:
        """Read and return the content from the static directory.

        Returns
        -------
        str
            The content of the static file.

        Raises
        ------
        FileNotFoundError
            If the file does not exist in the static/ directory.
        """
        file_path = os.path.join(STATIC_DIR, self._name)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(
                f"Header file '{self._name}' not found in static/"
            )
        with open(file_path) as f:
            return f.read()


class _HeaderSet:
    """A collection of header files for an ecFlow suite (internal use)."""

    def __init__(
        self,
        head_path: str = None,
        tail_path: str = None,
        envir_path: str = None
    ):
        # Create appropriate header objects based on provided paths
        if head_path:
            self._head = _FileHeader(DEFAULT_HEAD, head_path)
        else:
            self._head = _StaticHeader(DEFAULT_HEAD)

        if tail_path:
            self._tail = _FileHeader(DEFAULT_TAIL, tail_path)
        else:
            self._tail = _StaticHeader(DEFAULT_TAIL)

        if envir_path:
            self._envir = _FileHeader(DEFAULT_ENVIR, envir_path)
        else:
            self._envir = _StaticHeader(DEFAULT_ENVIR)

    @property
    def head(self) -> _Header:
        """Header: The head.h header object."""
        return self._head

    @property
    def tail(self) -> _Header:
        """Header: The tail.h header object."""
        return self._tail

    @property
    def envir(self) -> _Header:
        """Header: The envir-p1.h header object."""
        return self._envir

    def install(self, include_dir: str) -> list:
        """Install all header files to the include directory.

        Parameters
        ----------
        include_dir : str
            The path to the suite's include/ directory.

        Returns
        -------
        list
            List of installed file paths.
        """
        installed = []
        for header in [self._head, self._tail, self._envir]:
            path = header.install(include_dir)
            installed.append(path)
        return installed


# ---------------------------------------------------------------------------
# Public API functions
# ---------------------------------------------------------------------------

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
    header = _StaticHeader(filename)
    return header.get_content()


def ensure_headers(
    include_dir: str,
    head_path: str = None,
    tail_path: str = None,
    envir_path: str = None
) -> list:
    """Ensure all required header files are present in the include directory.

    If custom paths are provided, those files will be used. Otherwise,
    files are copied from the package's static/ directory.

    When no custom paths are provided and files already exist in the include
    directory, they will not be overwritten (backward compatible behavior).
    When custom paths are provided, files will always be copied/overwritten.

    Parameters
    ----------
    include_dir : str
        The path to the suite's include/ directory.
    head_path : str, optional
        Custom path to head.h file. If None, uses default from static/.
    tail_path : str, optional
        Custom path to tail.h file. If None, uses default from static/.
    envir_path : str, optional
        Custom path to envir-p1.h file. If None, uses default from static/.

    Returns
    -------
    list
        A list of filenames that were copied (empty if all files existed).

    Examples
    --------
    Using default headers (backward compatible):

    >>> copied = ensure_headers('/path/to/suite/include')
    >>> if copied:
    ...     print(f"Copied: {copied}")
    ... else:
    ...     print("All headers already present")

    Using custom header files:

    >>> copied = ensure_headers(
    ...     '/path/to/suite/include',
    ...     head_path='/custom/head.h',
    ...     tail_path='/custom/tail.h'
    ... )
    """
    copied_files = []

    # Create include directory if it doesn't exist
    if not os.path.exists(include_dir):
        os.makedirs(include_dir, exist_ok=True)

    # Build list of (header_file_name, custom_path) tuples
    header_configs = [
        (DEFAULT_HEAD, head_path),
        (DEFAULT_TAIL, tail_path),
        (DEFAULT_ENVIR, envir_path),
    ]

    for header_name, custom_path in header_configs:
        dest_path = os.path.join(include_dir, header_name)

        # Determine if we should copy/install this header
        # - If custom path provided: always install (user wants their file)
        # - If no custom path: only install if file doesn't exist (backward compat)
        should_install = custom_path is not None or not os.path.isfile(dest_path)

        if should_install:
            if custom_path:
                header = _FileHeader(header_name, custom_path)
            else:
                header = _StaticHeader(header_name)

            header.install(include_dir)
            copied_files.append(header_name)

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
