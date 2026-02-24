"""Tests for workflow header module.

This module contains pytest tests for the workflow_header.py functions,
verifying that header files are correctly read, copied, and managed.
"""

import os

import pytest

from pyecflow.workflow_header import (
    HEADER_FILES,
    STATIC_DIR,
    ensure_headers,
    headers_exist,
    list_missing_headers,
    read_static_file,
)


class TestHeaderFilesConstant:
    """Test the HEADER_FILES constant."""

    def test_header_files_contains_expected_files(self):
        """Test that HEADER_FILES contains the three required header files."""
        assert 'head.h' in HEADER_FILES
        assert 'envir-p1.h' in HEADER_FILES
        assert 'tail.h' in HEADER_FILES
        assert len(HEADER_FILES) == 3

    def test_static_dir_exists(self):
        """Test that the STATIC_DIR path exists."""
        assert os.path.isdir(STATIC_DIR)


class TestReadStaticFile:
    """Test the read_static_file function."""

    def test_read_head_file(self):
        """Test that head.h can be read and contains expected content."""
        content = read_static_file('head.h')
        assert content.startswith('#')
        assert 'ECF_NAME' in content

    def test_read_tail_file(self):
        """Test that tail.h can be read and contains expected content."""
        content = read_static_file('tail.h')
        assert content.startswith('#')
        assert 'ecflow_client' in content

    def test_read_envir_file(self):
        """Test that envir-p1.h can be read."""
        content = read_static_file('envir-p1.h')
        assert len(content) > 0

    def test_read_nonexistent_file_raises_error(self):
        """Test that reading a nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError) as excinfo:
            read_static_file('nonexistent_file.h')
        assert 'nonexistent_file.h' in str(excinfo.value)
        assert 'not found in static' in str(excinfo.value)


class TestEnsureHeaders:
    """Test the ensure_headers function."""

    def test_creates_directory_if_not_exists(self, tmp_path):
        """Test that ensure_headers creates the include directory if missing."""
        include_dir = tmp_path / 'include'
        assert not include_dir.exists()

        print(f"\nCreating include directory: {include_dir}")
        copied = ensure_headers(str(include_dir))
        print(f"Header files copied: {copied}")

        assert include_dir.exists()
        assert include_dir.is_dir()

    def test_copies_all_headers_to_empty_directory(self, tmp_path):
        """Test that all header files are copied to an empty directory."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        print(f"\nCopying headers to empty directory: {include_dir}")
        copied = ensure_headers(str(include_dir))
        print(f"Header files copied: {copied}")

        assert len(copied) == 3
        for header in HEADER_FILES:
            assert (include_dir / header).exists()

    def test_returns_list_of_copied_files(self, tmp_path):
        """Test that ensure_headers returns the list of copied filenames."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        copied = ensure_headers(str(include_dir))

        assert set(copied) == set(HEADER_FILES)

    def test_does_not_overwrite_existing_files(self, tmp_path):
        """Test that existing header files are not overwritten."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        # Create head.h with custom content
        custom_content = '# Custom head.h content'
        (include_dir / 'head.h').write_text(custom_content)

        print(f"\nCopying headers (head.h already exists): {include_dir}")
        copied = ensure_headers(str(include_dir))
        print(f"Header files copied (should skip head.h): {copied}")

        # head.h should not be in the copied list
        assert 'head.h' not in copied
        # head.h should retain custom content
        assert (include_dir / 'head.h').read_text() == custom_content
        # Other files should be copied
        assert 'tail.h' in copied
        assert 'envir-p1.h' in copied

    def test_second_call_copies_nothing(self, tmp_path):
        """Test that calling ensure_headers twice doesn't copy files again."""
        include_dir = tmp_path / 'include'

        # First call - should copy all files
        print(f"\nFirst call to ensure_headers: {include_dir}")
        first_copied = ensure_headers(str(include_dir))
        print(f"Header files copied (first call): {first_copied}")
        assert len(first_copied) == 3

        # Second call - should copy nothing
        print(f"Second call to ensure_headers: {include_dir}")
        second_copied = ensure_headers(str(include_dir))
        print(f"Header files copied (second call, should be empty): {second_copied}")
        assert len(second_copied) == 0

    def test_copied_files_have_correct_content(self, tmp_path):
        """Test that copied files have the same content as static files."""
        include_dir = tmp_path / 'include'

        print(f"\nCopying headers to verify content: {include_dir}")
        copied = ensure_headers(str(include_dir))
        print(f"Header files copied: {copied}")

        for header in HEADER_FILES:
            original = read_static_file(header)
            copied = (include_dir / header).read_text()
            assert copied == original


class TestHeadersExist:
    """Test the headers_exist function."""

    def test_returns_true_when_all_headers_exist(self, tmp_path):
        """Test that headers_exist returns True when all headers are present."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        # Create all header files
        for header in HEADER_FILES:
            (include_dir / header).write_text('# content')

        assert headers_exist(str(include_dir)) is True

    def test_returns_false_when_any_header_missing(self, tmp_path):
        """Test that headers_exist returns False when any header is missing."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        # Create only two header files (missing tail.h)
        (include_dir / 'head.h').write_text('# content')
        (include_dir / 'envir-p1.h').write_text('# content')

        assert headers_exist(str(include_dir)) is False

    def test_returns_false_for_nonexistent_directory(self, tmp_path):
        """Test that headers_exist returns False for non-existent directory."""
        include_dir = tmp_path / 'nonexistent'

        assert headers_exist(str(include_dir)) is False

    def test_returns_false_for_empty_directory(self, tmp_path):
        """Test that headers_exist returns False for empty directory."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        assert headers_exist(str(include_dir)) is False


class TestListMissingHeaders:
    """Test the list_missing_headers function."""

    def test_returns_all_headers_for_empty_directory(self, tmp_path):
        """Test that all headers are listed as missing for empty directory."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        missing = list_missing_headers(str(include_dir))

        assert set(missing) == set(HEADER_FILES)

    def test_returns_empty_list_when_all_exist(self, tmp_path):
        """Test that empty list is returned when all headers exist."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        # Create all header files
        for header in HEADER_FILES:
            (include_dir / header).write_text('# content')

        missing = list_missing_headers(str(include_dir))

        assert missing == []

    def test_returns_subset_of_missing_headers(self, tmp_path):
        """Test that only missing headers are returned when some exist."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        # Create only head.h
        (include_dir / 'head.h').write_text('# content')

        missing = list_missing_headers(str(include_dir))

        assert 'head.h' not in missing
        assert 'tail.h' in missing
        assert 'envir-p1.h' in missing
        assert len(missing) == 2

    def test_returns_all_for_nonexistent_directory(self, tmp_path):
        """Test that all headers are listed as missing for non-existent dir."""
        include_dir = tmp_path / 'nonexistent'

        missing = list_missing_headers(str(include_dir))

        assert set(missing) == set(HEADER_FILES)
