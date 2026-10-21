"""
Tests for xenco.batch module.
"""

import pytest
from xenco.batch import (
    find_files, encode_batch, decode_combined, BatchEncodingError,
    _make_file_header
)
from xenco.keyfile import KeyFile
from xenco.keygen import KeyGenerator


class TestFindFiles:
    """Test file discovery."""

    def test_find_files_top_level(self, temp_dir):
        """Test finding top-level files only."""
        (temp_dir / "a.txt").write_text("hello")
        (temp_dir / "b.txt").write_text("world")
        (temp_dir / "c.xenco").write_text("encoded")

        files = find_files(temp_dir, recursive=False)
        assert sorted(f.name for f in files) == ["a.txt", "b.txt"]

    def test_find_files_recursive(self, temp_dir):
        """Test recursive file discovery."""
        (temp_dir / "a.txt").write_text("hello")
        sub = temp_dir / "sub"
        sub.mkdir()
        (sub / "b.txt").write_text("world")

        files = find_files(temp_dir, recursive=True)
        assert sorted(f.name for f in files) == ["a.txt", "b.txt"]

    def test_find_files_invalid_path(self, temp_dir):
        """Test invalid directory raises error."""
        with pytest.raises(BatchEncodingError):
            find_files(temp_dir / "nonexistent")

    def test_find_files_exclude_files(self, temp_dir):
        """Test excluding specific files."""
        (temp_dir / "a.txt").write_text("hello")
        (temp_dir / "b.txt").write_text("world")

        files = find_files(temp_dir, recursive=False, exclude_files=("b.txt",))
        assert sorted(f.name for f in files) == ["a.txt"]

    def test_find_files_exclude_dirs(self, temp_dir):
        """Test excluding directories."""
        (temp_dir / "a.txt").write_text("hello")
        sub = temp_dir / "sub"
        sub.mkdir()
        (sub / "b.txt").write_text("world")

        files = find_files(temp_dir, recursive=True, exclude_dirs=("sub",))
        assert sorted(f.name for f in files) == ["a.txt"]

    def test_find_files_exclude_extensions(self, temp_dir):
        """Test excluding extensions."""
        (temp_dir / "a.txt").write_text("hello")
        (temp_dir / "b.log").write_text("log")

        files = find_files(temp_dir, recursive=False, exclude_extensions=(".log", "tmp"))
        assert sorted(f.name for f in files) == ["a.txt"]

    def test_find_files_exclude_relative_path(self, temp_dir):
        """Test excluding by relative path."""
        sub = temp_dir / "sub"
        sub.mkdir()
        (sub / "a.txt").write_text("hello")
        (sub / "b.txt").write_text("world")

        files = find_files(temp_dir, recursive=True, exclude_files=("sub/b.txt",))
        assert sorted(f.name for f in files) == ["a.txt"]


class TestBatchEncoding:
    """Test batch encoding operations."""

    def _make_keyfile(self, tmp_path):
        """Helper to create a usable key file."""
        source = (
            "The quick brown fox jumps over the lazy dog. "
            "1234567890 !@#$%^&*() "
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
            "abcdefghijklmnopqrstuvwxyz "
            "~`[]{}|\\;:\"\u003c\u003e,./? "
        )
        key_path = tmp_path / "key.xenco"
        keygen = KeyGenerator(32, 127)
        keyfile = KeyFile.from_keygenerator(keygen, source)
        keyfile.save(str(key_path))
        return str(key_path)

    def test_encode_batch_separate(self, tmp_path):
        """Test separate mode batch encoding."""
        key_path = self._make_keyfile(tmp_path)

        source_dir = tmp_path / "src"
        source_dir.mkdir()
        (source_dir / "a.txt").write_text("Hello, World!")
        (source_dir / "b.txt").write_text("Second file")

        result = encode_batch(source_dir, key_path, mode="separate")

        assert result["mode"] == "separate"
        assert result["count"] == 2
        assert sorted(result["files"]) == ["a.txt", "b.txt"]
        assert (source_dir / "a.txt.xenco").exists()
        assert (source_dir / "b.txt.xenco").exists()

    def test_encode_batch_separate_output_dir(self, tmp_path):
        """Test separate mode with custom output directory."""
        key_path = self._make_keyfile(tmp_path)

        source_dir = tmp_path / "src"
        source_dir.mkdir()
        out_dir = tmp_path / "out"
        (source_dir / "a.txt").write_text("Hello")

        result = encode_batch(source_dir, key_path, output=str(out_dir), mode="separate")

        assert result["output"] == str(out_dir)
        assert (out_dir / "a.txt.xenco").exists()

    def test_encode_batch_one(self, tmp_path):
        """Test one combined output mode."""
        key_path = self._make_keyfile(tmp_path)

        source_dir = tmp_path / "src"
        source_dir.mkdir()
        (source_dir / "a.txt").write_text("Hello, World!")
        (source_dir / "b.txt").write_text("Second file")

        out_file = tmp_path / "combined.xenco"
        result = encode_batch(source_dir, key_path, output=str(out_file), mode="one")

        assert result["mode"] == "one"
        assert result["count"] == 2
        assert out_file.exists()

    def test_encode_batch_no_files(self, tmp_path):
        """Test empty directory raises error."""
        key_path = self._make_keyfile(tmp_path)
        source_dir = tmp_path / "src"
        source_dir.mkdir()

        with pytest.raises(BatchEncodingError):
            encode_batch(source_dir, key_path)

    def test_encode_batch_overwrite(self, tmp_path):
        """Test overwrite flag."""
        key_path = self._make_keyfile(tmp_path)
        source_dir = tmp_path / "src"
        source_dir.mkdir()
        (source_dir / "a.txt").write_text("Hello")
        out_file = source_dir / "a.txt.xenco"
        out_file.write_text("old")

        result = encode_batch(source_dir, key_path, mode="separate", overwrite=True)
        assert result["count"] == 1
        assert out_file.read_text() != "old"

    def test_encode_batch_skips_key_file(self, tmp_path):
        """Test the key file inside the directory is not encoded."""
        source_dir = tmp_path / "src"
        source_dir.mkdir()
        source = "The quick brown fox jumps over the lazy dog. 1234567890 !@#$%^&*() ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz ~`[]{}|\\;:\"\u003c\u003e,./? "
        key_path = source_dir / "key.xenco"
        keygen = KeyGenerator(32, 127)
        keyfile = KeyFile.from_keygenerator(keygen, source)
        keyfile.save(str(key_path))

        (source_dir / "a.txt").write_text("Hello")

        result = encode_batch(source_dir, str(key_path), mode="separate")
        assert result["count"] == 1
        assert result["files"] == ["a.txt"]

    def test_encode_batch_dry_run_separate(self, tmp_path):
        """Test dry-run does not create separate output files."""
        key_path = self._make_keyfile(tmp_path)
        source_dir = tmp_path / "src"
        source_dir.mkdir()
        (source_dir / "a.txt").write_text("Hello")

        result = encode_batch(source_dir, key_path, mode="separate", dry_run=True, quiet=True)

        assert result["dry_run"] is True
        assert result["count"] == 1
        assert not (source_dir / "a.txt.xenco").exists()
        assert result["bytes_written"] == 0

    def test_encode_batch_dry_run_one(self, tmp_path):
        """Test dry-run does not create combined output file."""
        key_path = self._make_keyfile(tmp_path)
        source_dir = tmp_path / "src"
        source_dir.mkdir()
        (source_dir / "a.txt").write_text("Hello")

        out_file = tmp_path / "combined.xenco"
        result = encode_batch(source_dir, key_path, output=str(out_file), mode="one", dry_run=True, quiet=True)

        assert result["dry_run"] is True
        assert result["count"] == 1
        assert not out_file.exists()
        assert result["bytes_written"] == 0


class TestDecodeCombined:
    """Test decoding combined batch output."""

    def _make_keyfile(self, tmp_path):
        source = (
            "The quick brown fox jumps over the lazy dog. "
            "1234567890 !@#$%^&*() "
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
            "abcdefghijklmnopqrstuvwxyz "
            "~`[]{}|\\;:\"\u003c\u003e,./? "
        )
        key_path = tmp_path / "key.xenco"
        keygen = KeyGenerator(32, 127)
        keyfile = KeyFile.from_keygenerator(keygen, source)
        keyfile.save(str(key_path))
        return str(key_path)

    def test_decode_combined_roundtrip(self, tmp_path):
        """Test combined output decodes back to original files."""
        key_path = self._make_keyfile(tmp_path)
        source_dir = tmp_path / "src"
        source_dir.mkdir()
        (source_dir / "a.txt").write_text("Hello, World!")
        (source_dir / "b.txt").write_text("Second file")

        out_file = tmp_path / "combined.xenco"
        encode_batch(source_dir, key_path, output=str(out_file), mode="one", quiet=True)

        encoded = out_file.read_text(encoding="utf-8")
        decoded = decode_combined(encoded, key_path)

        assert sorted(decoded) == [
            ("a.txt", b"Hello, World!"),
            ("b.txt", b"Second file"),
        ]

    def test_make_file_header(self):
        """Test header format."""
        header = _make_file_header("path/to/file.txt", 42)
        assert header.startswith(b"XENCO_FILE\x1f")
        assert header.endswith(b"\n")
        assert b"path/to/file.txt\x1f42" in header
