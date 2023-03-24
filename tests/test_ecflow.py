import os
import pyecFlow


def test_ecflow_dir():

    ecflow_dir = os.environ.get('ECFLOW_DIR', 'undefined')
    print(f"ECFLOW_DIR = {ecflow_dir}")
    assert ecflow_dir != "undefined"
