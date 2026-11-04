import pytest
from harness.tools.workspace import WorkspaceTool

def test_write_and_read(tmp_path):
    tool = WorkspaceTool(tmp_path)
    tool.write("notes/demo.txt", "hello")
    assert tool.read("notes/demo.txt") == "hello"

def test_blocks_path_traversal(tmp_path):
    tool = WorkspaceTool(tmp_path)
    with pytest.raises(ValueError):
        tool.write("../outside.txt", "bad")

def test_blocks_unapproved_extension(tmp_path):
    tool = WorkspaceTool(tmp_path)
    with pytest.raises(ValueError):
        tool.write("payload.exe", "bad")
