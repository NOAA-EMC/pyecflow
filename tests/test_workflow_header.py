"""Tests for workflow header module.

This module contains pytest tests for the workflow_header.py functions,
verifying that header files are correctly read, copied, and managed.
"""

import os

import pytest

from pyecflow.workflow_header import (
    HEADER_FILES,
    STATIC_DIR,
    _FileHeader,
    _HeaderSet,
    _StaticHeader,
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


class Test_StaticHeader:
    """Test the _StaticHeader class."""

    def test_get_content_reads_head_file(self):
        """Test that _StaticHeader can read head.h from static/."""
        header = _StaticHeader('head.h')
        content = header.get_content()
        assert content.startswith('#')
        assert 'ECF_NAME' in content

    def test_get_content_reads_tail_file(self):
        """Test that _StaticHeader can read tail.h from static/."""
        header = _StaticHeader('tail.h')
        content = header.get_content()
        assert 'ecflow_client' in content

    def test_name_property(self):
        """Test the name property returns the header filename."""
        header = _StaticHeader('head.h')
        assert header.name == 'head.h'

    def test_install_creates_file(self, tmp_path):
        """Test that install creates the header file in include directory."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        header = _StaticHeader('head.h')
        result = header.install(str(include_dir))

        assert (include_dir / 'head.h').exists()
        assert result == str(include_dir / 'head.h')

    def test_install_creates_directory_if_needed(self, tmp_path):
        """Test that install creates include directory if it doesn't exist."""
        include_dir = tmp_path / 'include'
        assert not include_dir.exists()

        header = _StaticHeader('head.h')
        header.install(str(include_dir))

        assert include_dir.exists()
        assert (include_dir / 'head.h').exists()

    def test_raises_for_nonexistent_static_file(self):
        """Test that _StaticHeader raises FileNotFoundError for missing file."""
        header = _StaticHeader('nonexistent.h')
        with pytest.raises(FileNotFoundError) as excinfo:
            header.get_content()
        assert 'not found in static' in str(excinfo.value)


class Test_FileHeader:
    """Test the _FileHeader class."""

    def test_get_content_reads_custom_file(self, tmp_path):
        """Test that _FileHeader reads content from custom file path."""
        custom_file = tmp_path / 'custom_head.h'
        custom_content = '# Custom header content\necho "Custom"'
        custom_file.write_text(custom_content)

        header = _FileHeader('head.h', str(custom_file))
        content = header.get_content()

        assert content == custom_content

    def test_path_property(self, tmp_path):
        """Test the path property returns the source file path."""
        custom_file = tmp_path / 'custom.h'
        custom_file.write_text('# content')

        header = _FileHeader('head.h', str(custom_file))
        assert header.path == str(custom_file)

    def test_install_copies_custom_file(self, tmp_path):
        """Test that install copies custom file to include directory."""
        custom_file = tmp_path / 'custom_head.h'
        custom_content = '# Custom header'
        custom_file.write_text(custom_content)

        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        header = _FileHeader('head.h', str(custom_file))
        header.install(str(include_dir))

        installed_content = (include_dir / 'head.h').read_text()
        assert installed_content == custom_content

    def test_raises_for_nonexistent_file(self, tmp_path):
        """Test that _FileHeader raises FileNotFoundError for missing file."""
        header = _FileHeader('head.h', '/nonexistent/path/head.h')
        with pytest.raises(FileNotFoundError) as excinfo:
            header.get_content()
        assert 'not found' in str(excinfo.value)


class Test_HeaderSet:
    """Test the _HeaderSet class."""

    def test_default_creates_static_headers(self):
        """Test that _HeaderSet with no args creates _StaticHeaders."""
        headers = _HeaderSet()

        assert isinstance(headers.head, _StaticHeader)
        assert isinstance(headers.tail, _StaticHeader)
        assert isinstance(headers.envir, _StaticHeader)

    def test_custom_paths_create_file_headers(self, tmp_path):
        """Test that _HeaderSet with custom paths creates _FileHeaders."""
        custom_head = tmp_path / 'head.h'
        custom_tail = tmp_path / 'tail.h'
        custom_envir = tmp_path / 'envir-p1.h'
        for f in [custom_head, custom_tail, custom_envir]:
            f.write_text('# content')

        headers = _HeaderSet(
            head_path=str(custom_head),
            tail_path=str(custom_tail),
            envir_path=str(custom_envir)
        )

        assert isinstance(headers.head, _FileHeader)
        assert isinstance(headers.tail, _FileHeader)
        assert isinstance(headers.envir, _FileHeader)

    def test_mixed_paths_creates_mixed_headers(self, tmp_path):
        """Test that _HeaderSet with some custom paths creates mixed headers."""
        custom_head = tmp_path / 'head.h'
        custom_head.write_text('# custom head')

        headers = _HeaderSet(head_path=str(custom_head))

        assert isinstance(headers.head, _FileHeader)
        assert isinstance(headers.tail, _StaticHeader)
        assert isinstance(headers.envir, _StaticHeader)

    def test_install_all_headers(self, tmp_path):
        """Test that install() installs all three header files."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        headers = _HeaderSet()
        installed = headers.install(str(include_dir))

        assert len(installed) == 3
        assert (include_dir / 'head.h').exists()
        assert (include_dir / 'tail.h').exists()
        assert (include_dir / 'envir-p1.h').exists()


class TestEnsureHeadersWithCustomPaths:
    """Test ensure_headers function with custom path arguments."""

    def test_custom_head_path(self, tmp_path):
        """Test that custom head_path copies custom file."""
        custom_head = tmp_path / 'custom_head.h'
        custom_content = '# Custom head content'
        custom_head.write_text(custom_content)

        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        copied = ensure_headers(str(include_dir), head_path=str(custom_head))

        assert 'head.h' in copied
        assert (include_dir / 'head.h').read_text() == custom_content

    def test_custom_tail_path(self, tmp_path):
        """Test that custom tail_path copies custom file."""
        custom_tail = tmp_path / 'custom_tail.h'
        custom_content = '# Custom tail content'
        custom_tail.write_text(custom_content)

        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        copied = ensure_headers(str(include_dir), tail_path=str(custom_tail))

        assert 'tail.h' in copied
        assert (include_dir / 'tail.h').read_text() == custom_content

    def test_custom_envir_path(self, tmp_path):
        """Test that custom envir_path copies custom file."""
        custom_envir = tmp_path / 'custom_envir.h'
        custom_content = '# Custom envir content'
        custom_envir.write_text(custom_content)

        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        copied = ensure_headers(str(include_dir), envir_path=str(custom_envir))

        assert 'envir-p1.h' in copied
        assert (include_dir / 'envir-p1.h').read_text() == custom_content

    def test_all_custom_paths(self, tmp_path):
        """Test that all custom paths are copied."""
        custom_head = tmp_path / 'custom_head.h'
        custom_tail = tmp_path / 'custom_tail.h'
        custom_envir = tmp_path / 'custom_envir.h'

        custom_head.write_text('# head')
        custom_tail.write_text('# tail')
        custom_envir.write_text('# envir')

        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        copied = ensure_headers(
            str(include_dir),
            head_path=str(custom_head),
            tail_path=str(custom_tail),
            envir_path=str(custom_envir)
        )

        assert set(copied) == {'head.h', 'tail.h', 'envir-p1.h'}
        assert (include_dir / 'head.h').read_text() == '# head'
        assert (include_dir / 'tail.h').read_text() == '# tail'
        assert (include_dir / 'envir-p1.h').read_text() == '# envir'

    def test_custom_path_overwrites_existing_file(self, tmp_path):
        """Test that custom path overwrites existing file in include dir."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        # Create existing head.h
        existing_head = include_dir / 'head.h'
        existing_head.write_text('# existing content')

        # Create custom head.h
        custom_head = tmp_path / 'custom_head.h'
        custom_content = '# new custom content'
        custom_head.write_text(custom_content)

        # Ensure headers with custom path - should overwrite
        copied = ensure_headers(str(include_dir), head_path=str(custom_head))

        assert 'head.h' in copied
        assert existing_head.read_text() == custom_content

    def test_mixed_custom_and_default(self, tmp_path):
        """Test mixing custom paths with defaults."""
        custom_head = tmp_path / 'custom_head.h'
        custom_head.write_text('# custom head')

        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        copied = ensure_headers(str(include_dir), head_path=str(custom_head))

        # Custom head should be copied
        assert 'head.h' in copied
        assert (include_dir / 'head.h').read_text() == '# custom head'

        # Default tail and envir should also be copied (from static/)
        assert 'tail.h' in copied
        assert 'envir-p1.h' in copied
        assert 'ecflow_client' in (include_dir / 'tail.h').read_text()

    def test_custom_path_file_not_found(self, tmp_path):
        """Test that FileNotFoundError is raised for nonexistent custom path."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        with pytest.raises(FileNotFoundError):
            ensure_headers(
                str(include_dir),
                head_path='/nonexistent/path/head.h'
            )
