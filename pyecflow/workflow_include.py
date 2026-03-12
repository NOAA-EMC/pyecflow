"""Workflow include module for pyecflow.

This module provides functions to manage include files for ecFlow suites.
head.h and tail.h are required by ecFlow. envir-p1.h is an optional NCO
extension that is only deployed when explicitly configured.

In ECMWF terminology, these are "includes" - files that get included into
ecFlow task scripts. head.h is the header, tail.h is the footer.

Functions
---------
ensure_includes
    Ensure all required include files are present in the include directory.
includes_exist
    Check if all required include files exist in the include directory.
list_missing_includes
    List include files that are missing from the include directory.
read_static_file
    Read the contents of a file from the package's static/ directory.
"""

import os

# Required include files (must be present in the include/ directory)
INCLUDE_FILES = ['head.h', 'tail.h']

# Path to the static/ directory relative to this file
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')

# Default include file names
DEFAULT_HEAD = 'head.h'
DEFAULT_TAIL = 'tail.h'
DEFAULT_ENVIR = 'envir-p1.h'  # Optional NCO extension


def _get_static_path(name: str) -> str:
    """Get the path to a file in the static/ directory.

    Parameters
    ----------
    name : str
        The name of the file.

    Returns
    -------
    str
        The full path to the file in the static/ directory.

    Raises
    ------
    FileNotFoundError
        If the file does not exist in the static/ directory.
    """
    path = os.path.join(STATIC_DIR, name)
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Include file '{name}' not found in static/"
        )
    return path


class _FileInclude:
    """Include file manager (internal use).

    Reads content from a specified file path and installs it to the
    suite's include directory.
    """

    def __init__(self, name: str, path: str):
        """Initialize a file include.

        Parameters
        ----------
        name : str
            The name of the include file (e.g., 'head.h').
        path : str
            Path to the source file.
        """
        self._name = name
        self._path = path

    @property
    def name(self) -> str:
        """str: The name of the include file."""
        return self._name

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
                f"Include source file '{self._path}' not found"
            )
        with open(self._path) as f:
            return f.read()

    def install(self, include_dir: str) -> str:
        """Install the include file to the include directory.

        Parameters
        ----------
        include_dir : str
            The path to the suite's include/ directory.

        Returns
        -------
        str
            The path to the installed include file.
        """
        if not os.path.exists(include_dir):
            os.makedirs(include_dir, exist_ok=True)

        dest_path = os.path.join(include_dir, self._name)
        content = self.get_content()
        with open(dest_path, 'w') as f:
            f.write(content)
        return dest_path


class _IncludeSet:
    """A collection of include files for an ecFlow suite (internal use)."""

    def __init__(
        self,
        head_path: str,
        tail_path: str,
        envir_path: str
    ):
        """Initialize the include set.

        Parameters
        ----------
        head_path : str
            Path to the head.h file.
        tail_path : str
            Path to the tail.h file.
        envir_path : str
            Path to the envir-p1.h file.
        """
        self._head = _FileInclude(DEFAULT_HEAD, head_path)
        self._tail = _FileInclude(DEFAULT_TAIL, tail_path)
        self._envir = _FileInclude(DEFAULT_ENVIR, envir_path)

    @property
    def head(self) -> _FileInclude:
        """_FileInclude: The head.h include object."""
        return self._head

    @property
    def tail(self) -> _FileInclude:
        """_FileInclude: The tail.h include object."""
        return self._tail

    @property
    def envir(self) -> _FileInclude:
        """_FileInclude: The envir-p1.h include object."""
        return self._envir

    def install(self, include_dir: str) -> list:
        """Install all include files to the include directory.

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
        for inc in [self._head, self._tail, self._envir]:
            path = inc.install(include_dir)
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
    static_path = _get_static_path(filename)
    with open(static_path) as f:
        return f.read()


def ensure_includes(
    include_dir: str,
    head_path: str = None,
    tail_path: str = None,
    envir_path: str = None
) -> list:
    """Ensure all required include files are present in the include directory.

    head.h and tail.h are required by ecFlow and will always be deployed
    (from custom paths or package defaults). envir-p1.h is an optional NCO
    extension and is only deployed when envir_path is explicitly provided.

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
        Custom path to envir-p1.h file. If None, envir-p1.h is NOT deployed
        (opt-in behavior for this NCO extension).

    Returns
    -------
    list
        A list of filenames that were copied (empty if all files existed).

    Examples
    --------
    Using default includes (head.h and tail.h only):

    >>> copied = ensure_includes('/path/to/suite/include')
    >>> if copied:
    ...     print(f"Copied: {copied}")
    ... else:
    ...     print("All includes already present")

    With NCO envir-p1.h extension:

    >>> copied = ensure_includes(
    ...     '/path/to/suite/include',
    ...     envir_path='/custom/envir-p1.h'  # or use default: static/envir-p1.h
    ... )
    """
    copied_files = []

    # Create include directory if it doesn't exist
    if not os.path.exists(include_dir):
        os.makedirs(include_dir, exist_ok=True)

    # Required includes: head.h and tail.h (always deployed)
    required_configs = [
        (DEFAULT_HEAD, head_path),
        (DEFAULT_TAIL, tail_path),
    ]

    for include_name, custom_path in required_configs:
        dest_path = os.path.join(include_dir, include_name)

        # Determine if we should copy/install this include
        # - If custom path provided: always install (user wants their file)
        # - If no custom path: only install if file doesn't exist (backward compat)
        should_install = custom_path is not None or not os.path.isfile(dest_path)

        if should_install:
            # Use custom path if provided, otherwise use default from static/
            source_path = custom_path if custom_path else _get_static_path(include_name)
            inc = _FileInclude(include_name, source_path)
            inc.install(include_dir)
            copied_files.append(include_name)

    # Optional include: envir-p1.h (only if envir_path is explicitly provided)
    if envir_path is not None:
        inc = _FileInclude(DEFAULT_ENVIR, envir_path)
        inc.install(include_dir)
        copied_files.append(DEFAULT_ENVIR)

    return copied_files


def includes_exist(include_dir: str) -> bool:
    """Check if all required include files exist in the include directory.

    Parameters
    ----------
    include_dir : str
        The path to the suite's include/ directory.

    Returns
    -------
    bool
        True if all include files exist, False otherwise.
    """
    for include_file in INCLUDE_FILES:
        if not os.path.isfile(os.path.join(include_dir, include_file)):
            return False
    return True


def list_missing_includes(include_dir: str) -> list:
    """List include files that are missing from the include directory.

    Parameters
    ----------
    include_dir : str
        The path to the suite's include/ directory.

    Returns
    -------
    list
        List of missing include filenames.
    """
    missing = []
    for include_file in INCLUDE_FILES:
        if not os.path.isfile(os.path.join(include_dir, include_file)):
            missing.append(include_file)
    return missing
