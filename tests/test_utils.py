"""
Tests for xenco.utils module.
"""

import pytest
from xenco.utils import (
    read_text_file, write_text_file, read_binary_file, write_binary_file,
    FileIOError, get_file_info, is_large_file
)


class TestFileOperations:
    """Test basic file operations."""
    
    def test_read_text_file(self, temp_dir):
        """Test reading text file."""
        test_file = temp_dir / "test.txt"
        test_content = "Hello, World!"
        test_file.write_text(test_content)
        
        result = read_text_file(str(test_file))
        assert result == test_content
    
    def test_read_text_file_not_found(self, temp_dir):
        """Test reading non-existent file raises error."""
        with pytest.raises(FileIOError):
            read_text_file(str(temp_dir / "nonexistent.txt"))
    
    def test_write_text_file(self, temp_dir):
        """Test writing text file."""
        test_file = temp_dir / "output.txt"
        content = "Test content"
        
        chars_written = write_text_file(str(test_file), content)
        assert chars_written == len(content)
        assert test_file.read_text() == content
    
    def test_write_text_file_creates_directories(self, temp_dir):
        """Test writing creates parent directories."""
        test_file = temp_dir / "subdir" / "output.txt"
        write_text_file(str(test_file), "content")
        assert test_file.exists()
    
    def test_read_binary_file(self, temp_dir):
        """Test reading binary file."""
        test_file = temp_dir / "test.bin"
        content = b"\\x00\\x01\\x02\\x03"
        test_file.write_bytes(content)
        
        result = read_binary_file(str(test_file))
        assert result == content
    
    def test_write_binary_file(self, temp_dir):
        """Test writing binary file."""
        test_file = temp_dir / "output.bin"
        content = b"\\x00\\x01\\x02\\x03"
        
        bytes_written = write_binary_file(str(test_file), content)
        assert bytes_written == len(content)
        assert test_file.read_bytes() == content


class TestFileInfo:
    """Test file information functions."""
    
    def test_get_file_info_existing(self, temp_dir):
        \"\"\"Test getting info for existing file.\"\"\"
        test_file = temp_dir / \"test.txt\"\n        test_file.write_text(\"content\")\n        \n        info = get_file_info(str(test_file))\n        assert info[\"exists\"] is True\n        assert \"size\" in info\n        assert \"path\" in info\n    \n    def test_get_file_info_nonexistent(self, temp_dir):\n        \"\"\"Test getting info for non-existent file.\"\"\"
n        info = get_file_info(str(temp_dir / \"nonexistent.txt\"))\n        assert info[\"exists\"] is False\n    \n    def test_is_large_file(self, temp_dir):\n        \"\"\"Test large file detection.\"\"\"
n        # Create small file\n        small_file = temp_dir / \"small.txt\"\n        small_file.write_text(\"small\")\n        assert is_large_file(str(small_file)) is False\n        \n        # Create large file (1MB + 1 byte)\n        large_file = temp_dir / \"large.txt\"\n        large_file.write_bytes(b\"x\" * (1024 * 1024 + 1))\n        assert is_large_file(str(large_file)) is True


class TestExceptions:
n    \"\"\"Test utility exceptions.\"\"\"
n    \n    def test_file_io_error(self):\n        \"\"\"Test FileIOError exception.\"\"\"
n        err = FileIOError(\"test error\")\n        assert \"test error\" in str(err)
