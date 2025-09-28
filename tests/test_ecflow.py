import subprocess


class TestEcflow:
    def test_ecflow_client(self):

        try:
            result = subprocess.run(['which', 'ecflow_client'], capture_output=True, check=True, text=True)
            assert True
            print(f"ecflow_client = {result.stdout.strip()}")
        except subprocess.CalledProcessError:
            assert False, "ecflow_client not found!"

    def test_ecflow_import(self):
        try:
            import ecflow
            version = ecflow.__version__
            assert True
            print(f"ecflow module imported successfully, version = {version}")
        except ImportError:
            assert False, "Failed to import ecflow module!"
