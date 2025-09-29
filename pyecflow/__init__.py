from __future__ import absolute_import

import importlib.resources


def read_package_file(filetype: str, filename: str) -> str:
    """Read a file from the package data.
    Parameters
    ----------
    filetype : str
        The type of file to read, either 'static' or 'templates'.
    filename : str
        The name of the file to read.
    Returns
    -------
    str
        The contents of the file.
    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    Exception
        If the filetype is not 'static' or 'templates'.
    """

    try:
        with importlib.resources.path("pyecflow", filetype) as data_path:
            file = data_path / filename
            contents = file.read_text()
            return contents
    except FileNotFoundError:
        raise FileNotFoundError(f"File {filename} not found in {filetype}.")
    except Exception as e:
        raise Exception(f"Error reading file {filename} in {filetype}: {e}")
