import subprocess
import pyecFlow


def test_ecflow_found():

    try:
        result = subprocess.run(['which', 'ecflow_client'], capture_output=True, check=True, text=True)
        assert True, f"ecflow_client = {result.stdout.strip()}"
    except subprocess.CalledProcessError:
        assert False, "ecflow_client not found!"
