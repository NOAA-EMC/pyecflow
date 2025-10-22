import os
import shutil
import tempfile

import pyflow as pf

from pyecflow import LOGGER as logger


def generate_suite(suite: pf.Suite,
                   name: str,
                   suite_dir: str = None,
                   headers: bool = False) -> None: # type: ignore
    """
    Generate ecflow suite scripts and definition file.

    Parameters
    ----------
    suite (Suite):
        The suite to generate.
    name (str):
        The name of the suite.
    suite_dir (str, optional):
        The suite directory to use. If None, a temporary
        directory will be created.
        Defaults to None.
    headers (bool, optional):
        Whether to include headers in the generated scripts.
        Defaults to False.
    """
    if suite_dir is None:
        suite_dir = tempfile.mkdtemp(prefix=f"suite_{name}_")

    logger.info(f"Staging suite to {suite_dir}")
    suite_dir = os.path.realpath(suite_dir)
    def_dir = os.path.join(suite_dir, "def")
    scripts_dir = os.path.join(suite_dir, "scripts")
    include_dir = os.path.join(suite_dir, "include")

    logger.info("Generating suite definition file:")
    suite_def = suite.ecflow_definition()
    suite_def.check()
    def_file = os.path.join(def_dir, f"{name}.def")
    suite_def.save_as_defs(def_file)
    logger.info(f"ecflow suite definition file written to: {def_file}")

    logger.info(f"Generating suite scripts:")
    if os.path.isdir(scripts_dir):
        shutil.rmtree(scripts_dir)
    suite.deploy_suite(path=scripts_dir, headers=headers)
    logger.info(f"Scripts written to: {scripts_dir}")
