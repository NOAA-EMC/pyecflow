import pytest

from pyecflow import read_package_file


class TestReadPackageFile:

    def test_package_file_does_not_exist(self):
        with pytest.raises(FileNotFoundError):
            _ = read_package_file("static", "non_existent_file.txt")

    def test_static_head_file(self):
        head = read_package_file("static", "head.h")
        assert head.startswith("#")

    def test_static_tail_file(self):
        tail = read_package_file("static", "tail.h")
        assert tail.startswith("#")

    def test_template_task_file(self):
        task = read_package_file("templates", "task.ecf.j2")
        assert len(task) > 0
