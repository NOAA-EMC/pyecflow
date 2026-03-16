"""Tests for ecFlow preprocessing validation.

This module tests that the generated .ecf files can be successfully
preprocessed by ecFlow's job creation system.
"""

import os
import subprocess

import ecflow
import pyflow as pf
import pytest
import yaml

from pyecflow import WorkflowSuite

# Path to test data files
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


# Check if ecflow_client is available by trying to create a LocalHost
# pyflow.LocalHost requires ecflow_client in PATH
try:
    _test_host = pf.LocalHost('_test')
    ECFLOW_CLIENT_AVAILABLE = True
    del _test_host
except (TypeError, FileNotFoundError):
    ECFLOW_CLIENT_AVAILABLE = False


@pytest.fixture
def preprocessing_config():
    """Load the preprocessing test configuration from YAML."""
    config_path = os.path.join(DATA_DIR, 'preprocessing_test_config.yaml')
    with open(config_path) as f:
        return yaml.safe_load(f)


@pytest.fixture
def custom_includes_config():
    """Load the custom includes test configuration from YAML."""
    config_path = os.path.join(DATA_DIR, 'preprocessing_custom_headers_config.yaml')
    with open(config_path) as f:
        return yaml.safe_load(f)


class TestEcfPreprocessing:
    """Test that ecFlow can preprocess the generated .ecf files.

    These tests validate that the generated suite files are compatible
    with ecFlow's job creation/preprocessing system.
    """

    @pytest.mark.skipif(
        not ECFLOW_CLIENT_AVAILABLE,
        reason="ecflow_client not found in PATH"
    )
    def test_ecf_preprocessing(self, tmp_path, preprocessing_config):
        """Test that ecFlow can preprocess the generated .ecf files.

        This test verifies that:
        1. The .def file can be loaded by ecFlow
        2. The .ecf files can be preprocessed (job creation check)
        3. All %include directives can be resolved
        4. All ecFlow variables are properly defined

        This catches issues like:
        - Missing %include files
        - Invalid ecFlow directives
        - Undefined variables
        """
        suite_dir = tmp_path / "testSuite"
        print(f"\nSuite directory: {suite_dir}")

        my_suite = WorkflowSuite(
            'testSuite',
            host=pf.LocalHost('localhost'),
            files=str(suite_dir / 'scripts')
        )
        my_suite.generate_tree(preprocessing_config)
        my_suite.generate_suite(suite_dir=str(suite_dir))

        # Load the generated .def file
        def_file = suite_dir / 'def' / 'testSuite.def'
        assert def_file.exists(), f"Definition file not found: {def_file}"

        defs = ecflow.Defs(str(def_file))
        print(f"\nLoaded definition file: {def_file}")

        # Set up job creation control
        job_dir = tmp_path / 'jobs'
        job_dir.mkdir(exist_ok=True)

        job_ctrl = ecflow.JobCreationCtrl()
        job_ctrl.set_dir_for_job_creation(str(job_dir))

        # Check job creation - this validates that ecFlow can preprocess
        # all .ecf files and resolve all %include directives
        result = defs.check_job_creation(job_ctrl)

        # Print any errors for debugging
        if result:
            print(f"\nJob creation check errors:\n{result}")

        # Assert no errors during job creation check
        # check_job_creation returns None on success, or an error string on failure
        assert result is None, f"ecFlow job creation check failed:\n{result}"

        print("\necFlow preprocessing validation passed!")

    @pytest.mark.skipif(
        not ECFLOW_CLIENT_AVAILABLE,
        reason="ecflow_client not found in PATH"
    )
    def test_ecf_preprocessing_with_custom_includes(self, tmp_path, custom_includes_config):
        """Test ecFlow preprocessing with custom include files.

        Validates that custom includes work correctly with ecFlow's
        preprocessor.
        """
        suite_dir = tmp_path / "testSuite"

        # Create valid custom includes that ecFlow can process
        custom_head = tmp_path / "custom_head.h"
        custom_tail = tmp_path / "custom_tail.h"
        custom_envir = tmp_path / "custom_envir.h"

        # Custom head with required ecFlow init
        custom_head.write_text("""# Custom head.h
echo "Starting job"
timeout 300 ecflow_client --init=${ECF_RID}
""")

        # Custom tail with required ecFlow complete
        custom_tail.write_text("""# Custom tail.h
timeout 300 ecflow_client --complete
trap 0
exit 0
""")

        # Custom envir
        custom_envir.write_text("""# Custom envir-p1.h
export MY_CUSTOM_VAR="custom_value"
""")

        # Inject custom include paths into config
        config = {
            'includes': {
                'head': str(custom_head),
                'tail': str(custom_tail),
                'envir': str(custom_envir)
            },
            **custom_includes_config
        }

        my_suite = WorkflowSuite(
            'testSuite',
            host=pf.LocalHost('localhost'),
            files=str(suite_dir / 'scripts')
        )
        my_suite.generate_tree(config)
        my_suite.generate_suite(suite_dir=str(suite_dir))

        # Verify custom includes were installed
        include_dir = suite_dir / 'include'
        assert "Custom head.h" in (include_dir / 'head.h').read_text()
        assert "Custom tail.h" in (include_dir / 'tail.h').read_text()
        assert "Custom envir-p1.h" in (include_dir / 'envir-p1.h').read_text()

        # Load and check job creation
        def_file = suite_dir / 'def' / 'testSuite.def'
        defs = ecflow.Defs(str(def_file))

        job_dir = tmp_path / 'jobs'
        job_dir.mkdir(exist_ok=True)
        job_ctrl = ecflow.JobCreationCtrl()
        job_ctrl.set_dir_for_job_creation(str(job_dir))

        result = defs.check_job_creation(job_ctrl)
        # check_job_creation returns None on success, or an error string on failure
        assert result is None, f"ecFlow job creation check failed with custom includes:\n{result}"

        print("\necFlow preprocessing with custom includes passed!")

    @pytest.mark.skipif(
        not ECFLOW_CLIENT_AVAILABLE,
        reason="ecflow_client not found in PATH"
    )
    def test_generated_scripts_have_valid_bash_syntax(self, tmp_path, preprocessing_config):
        """Test that generated .ecf scripts have valid bash syntax.

        This test validates that the .ecf scripts, when preprocessed
        (include directives expanded, ecFlow directives stripped),
        contain valid bash syntax. It uses 'bash -n' to check syntax
        without executing the scripts.

        This catches:
        - Unclosed quotes
        - Missing fi, done, esac
        - Invalid bash syntax

        This does NOT catch:
        - Undefined variables (bash allows them)
        - Commands that don't exist
        - Logic errors
        """
        suite_dir = tmp_path / "testSuite"

        # Generate suite
        my_suite = WorkflowSuite(
            'testSuite',
            host=pf.LocalHost('localhost'),
            files=str(suite_dir / 'scripts')
        )
        my_suite.generate_tree(preprocessing_config)
        my_suite.generate_suite(suite_dir=str(suite_dir))

        # Find all generated .ecf files
        scripts_dir = suite_dir / 'scripts'
        include_dir = suite_dir / 'include'
        ecf_files = list(scripts_dir.rglob("*.ecf"))
        assert ecf_files, "No .ecf files were generated"

        print(f"\nFound {len(ecf_files)} .ecf files to validate")

        # Preprocess and validate bash syntax for each .ecf file
        for ecf_file in ecf_files:
            # Read the .ecf file
            content = ecf_file.read_text()

            # Expand %include directives
            missing_includes = []

            def expand_includes(text, inc_dir):
                """Expand %include <file.h> directives with actual content."""
                import re
                pattern = r'%include\s+<([^>]+)>'

                def replacer(match):
                    inc_file = inc_dir / match.group(1)
                    if inc_file.exists():
                        return inc_file.read_text()
                    # Track missing includes so the test can fail explicitly
                    missing_includes.append(str(inc_file))
                    return f"# Include not found: {match.group(1)}"

                return re.sub(pattern, replacer, text)

            preprocessed = expand_includes(content, include_dir)

            # Fail if any include files were missing
            if missing_includes:
                pytest.fail(
                    f"Missing include files for {ecf_file.name}: "
                    f"{', '.join(missing_includes)}"
                )

            # Strip ecFlow-specific directives for bash validation
            # Remove %nopp, %end, %manual, %comment, %ecf_*, etc.
            import re
            preprocessed = re.sub(r'^%nopp\s*$', '', preprocessed, flags=re.MULTILINE)
            preprocessed = re.sub(r'^%end\s*$', '', preprocessed, flags=re.MULTILINE)
            preprocessed = re.sub(r'^%manual\s*$', '# manual section', preprocessed, flags=re.MULTILINE)
            preprocessed = re.sub(r'^%comment\s*$', '#', preprocessed, flags=re.MULTILINE)

            # Write preprocessed content to temp file for bash validation.
            # Use the relative path from scripts_dir to ensure uniqueness.
            relative_path = ecf_file.relative_to(scripts_dir)
            job_name = str(relative_path).replace(os.sep, "_")
            job_file = tmp_path / f"{job_name}.job"
            job_file.write_text(preprocessed)

            result = subprocess.run(
                ["bash", "-n", str(job_file)],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, \
                f"Bash syntax error in {ecf_file.name}:\n{result.stderr}"
            print(f"  {ecf_file.name}: syntax OK")

        print(f"\nValidated bash syntax for {len(ecf_files)} .ecf files")
