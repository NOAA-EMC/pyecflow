"""Tests for workflow include module.

This module contains pytest tests for the workflow_include.py functions,
verifying that include files are correctly read, copied, and managed.
"""

import os

import pytest

from pyecflow.workflow_include import (
    INCLUDE_FILES,
    STATIC_DIR,
    _FileInclude,
    _IncludeSet,
    _StaticInclude,
    ensure_includes,
    includes_exist,
    list_missing_includes,
    read_static_file,
)


class TestIncludeFilesConstant:
    """Test the INCLUDE_FILES constant."""

    def test_include_files_contains_expected_files(self):
        """Test that INCLUDE_FILES contains the three required include files."""
        assert 'head.h' in INCLUDE_FILES
        assert 'envir-p1.h' in INCLUDE_FILES
        assert 'tail.h' in INCLUDE_FILES
        assert len(INCLUDE_FILES) == 3

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


class TestEnsureIncludes:
    """Test the ensure_includes function."""

    def test_creates_directory_if_not_exists(self, tmp_path):
        """Test that ensure_includes creates the include directory if missing."""
        include_dir = tmp_path / 'include'
        assert not include_dir.exists()

        print(f"\nCreating include directory: {include_dir}")
        copied = ensure_includes(str(include_dir))
        print(f"Include files copied: {copied}")

        assert include_dir.exists()
        assert include_dir.is_dir()

    def test_copies_all_includes_to_empty_directory(self, tmp_path):
        """Test that all include files are copied to an empty directory."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        print(f"\nCopying includes to empty directory: {include_dir}")
        copied = ensure_includes(str(include_dir))
        print(f"Include files copied: {copied}")

        assert len(copied) == 3
        for inc in INCLUDE_FILES:
            assert (include_dir / inc).exists()

    def test_returns_list_of_copied_files(self, tmp_path):
        """Test that ensure_includes returns the list of copied filenames."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        copied = ensure_includes(str(include_dir))

        assert set(copied) == set(INCLUDE_FILES)

    def test_does_not_overwrite_existing_files(self, tmp_path):
        """Test that existing include files are not overwritten."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        # Create head.h with custom content
        custom_content = '# Custom head.h content'
        (include_dir / 'head.h').write_text(custom_content)

        print(f"\nCopying includes (head.h already exists): {include_dir}")
        copied = ensure_includes(str(include_dir))
        print(f"Include files copied (should skip head.h): {copied}")

        # head.h should not be in the copied list
        assert 'head.h' not in copied
        # head.h should retain custom content
        assert (include_dir / 'head.h').read_text() == custom_content
        # Other files should be copied
        assert 'tail.h' in copied
        assert 'envir-p1.h' in copied

    def test_second_call_copies_nothing(self, tmp_path):
        """Test that calling ensure_includes twice doesn't copy files again."""
        include_dir = tmp_path / 'include'

        # First call - should copy all files
        print(f"\nFirst call to ensure_includes: {include_dir}")
        first_copied = ensure_includes(str(include_dir))
        print(f"Include files copied (first call): {first_copied}")
        assert len(first_copied) == 3

        # Second call - should copy nothing
        print(f"Second call to ensure_includes: {include_dir}")
        second_copied = ensure_includes(str(include_dir))
        print(f"Include files copied (second call, should be empty): {second_copied}")
        assert len(second_copied) == 0

    def test_copied_files_have_correct_content(self, tmp_path):
        """Test that copied files have the same content as static files."""
        include_dir = tmp_path / 'include'

        print(f"\nCopying includes to verify content: {include_dir}")
        copied = ensure_includes(str(include_dir))
        print(f"Include files copied: {copied}")

        for inc in INCLUDE_FILES:
            original = read_static_file(inc)
            file_content = (include_dir / inc).read_text()
            assert file_content == original


class TestIncludesExist:
    """Test the includes_exist function."""

    def test_returns_true_when_all_includes_exist(self, tmp_path):
        """Test that includes_exist returns True when all includes are present."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        # Create all include files
        for inc in INCLUDE_FILES:
            (include_dir / inc).write_text('# content')

        assert includes_exist(str(include_dir)) is True

    def test_returns_false_when_any_include_missing(self, tmp_path):
        """Test that includes_exist returns False when any include is missing."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        # Create only two include files (missing tail.h)
        (include_dir / 'head.h').write_text('# content')
        (include_dir / 'envir-p1.h').write_text('# content')

        assert includes_exist(str(include_dir)) is False

    def test_returns_false_for_nonexistent_directory(self, tmp_path):
        """Test that includes_exist returns False for non-existent directory."""
        include_dir = tmp_path / 'nonexistent'

        assert includes_exist(str(include_dir)) is False

    def test_returns_false_for_empty_directory(self, tmp_path):
        """Test that includes_exist returns False for empty directory."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        assert includes_exist(str(include_dir)) is False


class TestListMissingIncludes:
    """Test the list_missing_includes function."""

    def test_returns_all_includes_for_empty_directory(self, tmp_path):
        """Test that all includes are listed as missing for empty directory."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        missing = list_missing_includes(str(include_dir))

        assert set(missing) == set(INCLUDE_FILES)

    def test_returns_empty_list_when_all_exist(self, tmp_path):
        """Test that empty list is returned when all includes exist."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        # Create all include files
        for inc in INCLUDE_FILES:
            (include_dir / inc).write_text('# content')

        missing = list_missing_includes(str(include_dir))

        assert missing == []

    def test_returns_subset_of_missing_includes(self, tmp_path):
        """Test that only missing includes are returned when some exist."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        # Create only head.h
        (include_dir / 'head.h').write_text('# content')

        missing = list_missing_includes(str(include_dir))

        assert 'head.h' not in missing
        assert 'tail.h' in missing
        assert 'envir-p1.h' in missing
        assert len(missing) == 2

    def test_returns_all_for_nonexistent_directory(self, tmp_path):
        """Test that all includes are listed as missing for non-existent dir."""
        include_dir = tmp_path / 'nonexistent'

        missing = list_missing_includes(str(include_dir))

        assert set(missing) == set(INCLUDE_FILES)


class Test_StaticInclude:
    """Test the _StaticInclude class."""

    def test_get_content_reads_head_file(self):
        """Test that _StaticInclude can read head.h from static/."""
        inc = _StaticInclude('head.h')
        content = inc.get_content()
        assert content.startswith('#')
        assert 'ECF_NAME' in content

    def test_get_content_reads_tail_file(self):
        """Test that _StaticInclude can read tail.h from static/."""
        inc = _StaticInclude('tail.h')
        content = inc.get_content()
        assert 'ecflow_client' in content

    def test_name_property(self):
        """Test the name property returns the include filename."""
        inc = _StaticInclude('head.h')
        assert inc.name == 'head.h'

    def test_install_creates_file(self, tmp_path):
        """Test that install creates the include file in include directory."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        inc = _StaticInclude('head.h')
        result = inc.install(str(include_dir))

        assert (include_dir / 'head.h').exists()
        assert result == str(include_dir / 'head.h')

    def test_install_creates_directory_if_needed(self, tmp_path):
        """Test that install creates include directory if it doesn't exist."""
        include_dir = tmp_path / 'include'
        assert not include_dir.exists()

        inc = _StaticInclude('head.h')
        inc.install(str(include_dir))

        assert include_dir.exists()
        assert (include_dir / 'head.h').exists()

    def test_raises_for_nonexistent_static_file(self):
        """Test that _StaticInclude raises FileNotFoundError for missing file."""
        inc = _StaticInclude('nonexistent.h')
        with pytest.raises(FileNotFoundError) as excinfo:
            inc.get_content()
        assert 'not found in static' in str(excinfo.value)


class Test_FileInclude:
    """Test the _FileInclude class."""

    def test_get_content_reads_custom_file(self, tmp_path):
        """Test that _FileInclude reads content from custom file path."""
        custom_file = tmp_path / 'custom_head.h'
        custom_content = '# Custom include content\necho "Custom"'
        custom_file.write_text(custom_content)

        inc = _FileInclude('head.h', str(custom_file))
        content = inc.get_content()

        assert content == custom_content

    def test_path_property(self, tmp_path):
        """Test the path property returns the source file path."""
        custom_file = tmp_path / 'custom.h'
        custom_file.write_text('# content')

        inc = _FileInclude('head.h', str(custom_file))
        assert inc.path == str(custom_file)

    def test_install_copies_custom_file(self, tmp_path):
        """Test that install copies custom file to include directory."""
        custom_file = tmp_path / 'custom_head.h'
        custom_content = '# Custom include'
        custom_file.write_text(custom_content)

        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        inc = _FileInclude('head.h', str(custom_file))
        inc.install(str(include_dir))

        installed_content = (include_dir / 'head.h').read_text()
        assert installed_content == custom_content

    def test_raises_for_nonexistent_file(self, tmp_path):
        """Test that _FileInclude raises FileNotFoundError for missing file."""
        inc = _FileInclude('head.h', '/nonexistent/path/head.h')
        with pytest.raises(FileNotFoundError) as excinfo:
            inc.get_content()
        assert 'not found' in str(excinfo.value)


class Test_IncludeSet:
    """Test the _IncludeSet class."""

    def test_default_creates_static_includes(self):
        """Test that _IncludeSet with no args creates _StaticIncludes."""
        includes = _IncludeSet()

        assert isinstance(includes.head, _StaticInclude)
        assert isinstance(includes.tail, _StaticInclude)
        assert isinstance(includes.envir, _StaticInclude)

    def test_custom_paths_create_file_includes(self, tmp_path):
        """Test that _IncludeSet with custom paths creates _FileIncludes."""
        custom_head = tmp_path / 'head.h'
        custom_tail = tmp_path / 'tail.h'
        custom_envir = tmp_path / 'envir-p1.h'
        for f in [custom_head, custom_tail, custom_envir]:
            f.write_text('# content')

        includes = _IncludeSet(
            head_path=str(custom_head),
            tail_path=str(custom_tail),
            envir_path=str(custom_envir)
        )

        assert isinstance(includes.head, _FileInclude)
        assert isinstance(includes.tail, _FileInclude)
        assert isinstance(includes.envir, _FileInclude)

    def test_mixed_paths_creates_mixed_includes(self, tmp_path):
        """Test that _IncludeSet with some custom paths creates mixed includes."""
        custom_head = tmp_path / 'head.h'
        custom_head.write_text('# custom head')

        includes = _IncludeSet(head_path=str(custom_head))

        assert isinstance(includes.head, _FileInclude)
        assert isinstance(includes.tail, _StaticInclude)
        assert isinstance(includes.envir, _StaticInclude)

    def test_install_all_includes(self, tmp_path):
        """Test that install() installs all three include files."""
        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        includes = _IncludeSet()
        installed = includes.install(str(include_dir))

        assert len(installed) == 3
        assert (include_dir / 'head.h').exists()
        assert (include_dir / 'tail.h').exists()
        assert (include_dir / 'envir-p1.h').exists()


class TestEnsureIncludesWithCustomPaths:
    """Test ensure_includes function with custom path arguments."""

    def test_custom_head_path(self, tmp_path):
        """Test that custom head_path copies custom file."""
        custom_head = tmp_path / 'custom_head.h'
        custom_content = '# Custom head content'
        custom_head.write_text(custom_content)

        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        copied = ensure_includes(str(include_dir), head_path=str(custom_head))

        assert 'head.h' in copied
        assert (include_dir / 'head.h').read_text() == custom_content

    def test_custom_tail_path(self, tmp_path):
        """Test that custom tail_path copies custom file."""
        custom_tail = tmp_path / 'custom_tail.h'
        custom_content = '# Custom tail content'
        custom_tail.write_text(custom_content)

        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        copied = ensure_includes(str(include_dir), tail_path=str(custom_tail))

        assert 'tail.h' in copied
        assert (include_dir / 'tail.h').read_text() == custom_content

    def test_custom_envir_path(self, tmp_path):
        """Test that custom envir_path copies custom file."""
        custom_envir = tmp_path / 'custom_envir.h'
        custom_content = '# Custom envir content'
        custom_envir.write_text(custom_content)

        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        copied = ensure_includes(str(include_dir), envir_path=str(custom_envir))

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

        copied = ensure_includes(
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

        # Ensure includes with custom path - should overwrite
        copied = ensure_includes(str(include_dir), head_path=str(custom_head))

        assert 'head.h' in copied
        assert existing_head.read_text() == custom_content

    def test_mixed_custom_and_default(self, tmp_path):
        """Test mixing custom paths with defaults."""
        custom_head = tmp_path / 'custom_head.h'
        custom_head.write_text('# custom head')

        include_dir = tmp_path / 'include'
        include_dir.mkdir()

        copied = ensure_includes(str(include_dir), head_path=str(custom_head))

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
            ensure_includes(
                str(include_dir),
                head_path='/nonexistent/path/head.h'
            )
