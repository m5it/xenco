"""
Tests for xenco.keyfile module.
"""

import json
import pytest
from xenco.keyfile import KeyFile, KeyFileError, KeyFileCorruptedError, KeyFileVersionError


class TestKeyFile:
    """Test KeyFile class."""
    
    def test_init(self, mock_key_mappings):
        """Test initialization."""
        encode_map, decode_map = mock_key_mappings
        keyfile = KeyFile(
            encode_map=encode_map,
            decode_map=decode_map,
            source="test_source",
            ascii_from=32,
            ascii_to=128
        )
        
        assert keyfile.version == "1.0.0"
        assert keyfile.source == "test_source"
        assert keyfile.ascii_from == 32
        assert keyfile.ascii_to == 128
        assert keyfile.encode_map == encode_map
    
    def test_to_dict(self, mock_key_mappings):
        """Test conversion to dictionary."""
        encode_map, decode_map = mock_key_mappings
        keyfile = KeyFile(
            encode_map=encode_map,
            decode_map=decode_map,
            source="test_source",
            ascii_from=32,
            ascii_to=128
        )
        
        data = keyfile.to_dict()
        
        assert "version" in data
        assert "created" in data
        assert "source" in data
        assert "ascii_range" in data
        assert "checksum" in data
        assert "encode_map" in data
        assert "decode_map" in data
        
        assert data["source"] == "test_source"
        assert data["ascii_range"]["from"] == 32
        assert data["ascii_range"]["to"] == 128
    
    def test_save_and_load(self, mock_key_mappings, temp_dir):
        """Test saving and loading key file."""
        encode_map, decode_map = mock_key_mappings
        keyfile = KeyFile(
            encode_map=encode_map,
            decode_map=decode_map,
            source="test_source",
            ascii_from=32,
            ascii_to=128
        )
        
        key_path = temp_dir / "test.xenco"
        keyfile.save(str(key_path))
        
        assert key_path.exists()
        
        # Load and verify
        loaded = KeyFile.load(str(key_path))
        assert loaded.source == "test_source"
        assert loaded.encode_map == encode_map
        assert loaded.get_decode_map_int() == decode_map
    
    def test_save_pretty(self, mock_key_mappings, temp_dir):
        """Test saving with pretty=True."""
        encode_map, decode_map = mock_key_mappings
        keyfile = KeyFile(
            encode_map=encode_map,
            decode_map=decode_map,
            source="test_source",
            ascii_from=32,
            ascii_to=128
        )
        
        key_path = temp_dir / "test.xenco"
        keyfile.save(str(key_path), pretty=True)
        
        # Check file is readable (has newlines from pretty printing)
        content = key_path.read_text()
        assert "\n" in content
    
    def test_load_corrupted(self, mock_key_mappings, temp_dir):
        """Test loading corrupted file raises error."""
        encode_map, decode_map = mock_key_mappings
        keyfile = KeyFile(
            encode_map=encode_map,
            decode_map=decode_map,
            source="test_source",
            ascii_from=32,
            ascii_to=128
        )
        
        key_path = temp_dir / "test.xenco"
        keyfile.save(str(key_path))
        
        # Corrupt the file
        data = json.loads(key_path.read_text())
        data["encode_map"]["A"] = "X"  # Change mapping
        key_path.write_text(json.dumps(data))
        
        with pytest.raises(KeyFileCorruptedError):
            KeyFile.load(str(key_path))
    
    def test_load_no_verify(self, mock_key_mappings, temp_dir):
        """Test loading with verify=False skips checksum."""
        encode_map, decode_map = mock_key_mappings
        keyfile = KeyFile(
            encode_map=encode_map,
            decode_map=decode_map,
            source="test_source",
            ascii_from=32,
            ascii_to=128
        )
        
        key_path = temp_dir / "test.xenco"
        keyfile.save(str(key_path))
        
        # Corrupt but still loadable without verification
        data = json.loads(key_path.read_text())
        data["encode_map"]["A"] = "X"
        key_path.write_text(json.dumps(data))
        
        # Should not raise with verify=False
        loaded = KeyFile.load(str(key_path), verify=False)
        assert loaded is not None
    
    def test_get_decode_map_int(self, mock_key_mappings):
        """Test getting decode map with integer keys."""
        encode_map, decode_map = mock_key_mappings
        keyfile = KeyFile(
            encode_map=encode_map,
            decode_map=decode_map,
            source="test_source",
            ascii_from=32,
            ascii_to=128
        )
        
        # decode_map should have string keys (for JSON)
        assert all(isinstance(k, str) for k in keyfile.decode_map.keys())
        
        # get_decode_map_int should return int keys
        int_map = keyfile.get_decode_map_int()
        assert all(isinstance(k, int) for k in int_map.keys())
        assert int_map == decode_map
    
    def test_inspect(self, mock_key_mappings):
        """Test inspect output."""
        encode_map, decode_map = mock_key_mappings
        keyfile = KeyFile(
            encode_map=encode_map,
            decode_map=decode_map,
            source="test_source",
            ascii_from=32,
            ascii_to=128
        )
        
        inspection = keyfile.inspect()
        assert "xEnco Key File Inspection" in inspection
        assert "test_source" in inspection
        assert "32 - 128" in inspection
        assert "64" in inspection  # Total mappings
    
    def test_get_metadata(self, mock_key_mappings):
        """Test getting metadata."""
        encode_map, decode_map = mock_key_mappings
        keyfile = KeyFile(
            encode_map=encode_map,
            decode_map=decode_map,
            source="test_source",
            ascii_from=32,
            ascii_to=128
        )
        
        meta = keyfile.get_metadata()
        assert "version" in meta
        assert "created" in meta
        assert "source" in meta
        assert "ascii_from" in meta
        assert "ascii_to" in meta
        assert "mapping_count" in meta
        assert meta["mapping_count"] == 64
    
    def test_from_keygenerator(self, sample_source_text, temp_dir):
        """Test creating KeyFile from KeyGenerator."""
        from xenco.keygen import KeyGenerator
        
        keygen = KeyGenerator(32, 127)
        keyfile = KeyFile.from_keygenerator(keygen, sample_source_text)
        
        assert keyfile.source == sample_source_text
        assert len(keyfile.encode_map) == 65
        assert keyfile.ascii_from == 32
        assert keyfile.ascii_to == 127


class TestKeyFileErrors:
    """Test KeyFile error conditions."""
    
    def test_keyfile_error_inheritance(self):
        """Test exception inheritance."""
        assert issubclass(KeyFileError, Exception)
        assert issubclass(KeyFileCorruptedError, KeyFileError)
        assert issubclass(KeyFileVersionError, KeyFileError)
    
    def test_load_nonexistent_file(self, temp_dir):
        """Test loading non-existent file."""
        with pytest.raises(KeyFileError):
            KeyFile.load(str(temp_dir / "nonexistent.xenco"))
    
    def test_load_invalid_json(self, temp_dir):
        """Test loading invalid JSON."""
        key_path = temp_dir / "invalid.xenco"
        key_path.write_text("not valid json")
        
        with pytest.raises(KeyFileError):
            KeyFile.load(str(key_path))
    
    def test_load_missing_required_fields(self, temp_dir):
        """Test loading file with missing fields."""
        key_path = temp_dir / "incomplete.xenco"
        key_path.write_text(json.dumps({"version": "1.0.0"}))
        
        with pytest.raises(KeyFileError):
            KeyFile.load(str(key_path))


class TestKeyFileMix:
    """Test KeyFile mix/remix functionality."""
    
    def test_mix_shift(self, mock_key_mappings):
        """Test mix with shift."""
        encode_map, decode_map = mock_key_mappings
        keyfile = KeyFile(
            encode_map=encode_map,
            decode_map=decode_map,
            source="test_source",
            ascii_from=32,
            ascii_to=128
        )
        
        base64_chars = list(encode_map.keys())
        original_values = [encode_map[b64] for b64 in base64_chars]
        
        mixed = keyfile.mix(shift=1)
        new_values = [mixed.encode_map[b64] for b64 in base64_chars]
        
        assert new_values == [original_values[-1]] + original_values[:-1]
        assert mixed.source == keyfile.source
        assert mixed.ascii_from == keyfile.ascii_from
        assert mixed.ascii_to == keyfile.ascii_to
        assert len(mixed.encode_map) == len(keyfile.encode_map)
    
    def test_mix_reverse(self, mock_key_mappings):
        """Test mix with reverse."""
        encode_map, decode_map = mock_key_mappings
        keyfile = KeyFile(
            encode_map=encode_map,
            decode_map=decode_map,
            source="test_source",
            ascii_from=32,
            ascii_to=128
        )
        
        base64_chars = list(encode_map.keys())
        original_values = [encode_map[b64] for b64 in base64_chars]
        
        mixed = keyfile.mix(reverse=True)
        new_values = [mixed.encode_map[b64] for b64 in base64_chars]
        
        assert new_values == list(reversed(original_values))
    
    def test_mix_seed_deterministic(self, mock_key_mappings):
        """Test mix with seed is deterministic."""
        encode_map, decode_map = mock_key_mappings
        keyfile = KeyFile(
            encode_map=encode_map,
            decode_map=decode_map,
            source="test_source",
            ascii_from=32,
            ascii_to=128
        )
        
        mixed1 = keyfile.mix(seed=12345)
        mixed2 = keyfile.mix(seed=12345)
        
        assert mixed1.encode_map == mixed2.encode_map
        assert mixed1.encode_map != encode_map
    
    def test_mix_permutation(self, mock_key_mappings):
        """Test mix with explicit permutation."""
        encode_map, decode_map = mock_key_mappings
        keyfile = KeyFile(
            encode_map=encode_map,
            decode_map=decode_map,
            source="test_source",
            ascii_from=32,
            ascii_to=128
        )
        
        base64_chars = list(encode_map.keys())
        original_values = [encode_map[b64] for b64 in base64_chars]
        permutation = list(reversed(range(len(original_values))))
        
        mixed = keyfile.mix(permutation=permutation)
        new_values = [mixed.encode_map[b64] for b64 in base64_chars]
        
        assert new_values == list(reversed(original_values))
    
    def test_mix_decode_map_consistent(self, mock_key_mappings):
        """Test mixed key has consistent decode map."""
        encode_map, decode_map = mock_key_mappings
        keyfile = KeyFile(
            encode_map=encode_map,
            decode_map=decode_map,
            source="test_source",
            ascii_from=32,
            ascii_to=128
        )
        
        mixed = keyfile.mix(shift=3)
        
        for b64_char, key_char in mixed.encode_map.items():
            assert mixed.get_decode_map_int()[ord(key_char)] == b64_char
    
    def test_mix_no_method_raises(self, mock_key_mappings):
        """Test mix with no method raises ValueError."""
        encode_map, decode_map = mock_key_mappings
        keyfile = KeyFile(
            encode_map=encode_map,
            decode_map=decode_map,
            source="test_source",
            ascii_from=32,
            ascii_to=128
        )
        
        with pytest.raises(ValueError):
            keyfile.mix()
    
    def test_mix_multiple_methods_raises(self, mock_key_mappings):
        """Test mix with multiple methods raises ValueError."""
        encode_map, decode_map = mock_key_mappings
        keyfile = KeyFile(
            encode_map=encode_map,
            decode_map=decode_map,
            source="test_source",
            ascii_from=32,
            ascii_to=128
        )
        
        with pytest.raises(ValueError):
            keyfile.mix(shift=1, reverse=True)
    
    def test_mix_invalid_permutation(self, mock_key_mappings):
        """Test mix with invalid permutation raises ValueError."""
        encode_map, decode_map = mock_key_mappings
        keyfile = KeyFile(
            encode_map=encode_map,
            decode_map=decode_map,
            source="test_source",
            ascii_from=32,
            ascii_to=128
        )
        
        with pytest.raises(ValueError):
            keyfile.mix(permutation=[0, 0])  # Duplicate / invalid
    
    def test_mix_changes_encoding(self, temp_dir, sample_source_text):
        """Test mixed key produces different but decodeable output."""
        from xenco.keygen import KeyGenerator
        from xenco.encoder import Encoder
        
        keygen = KeyGenerator(32, 127)
        keyfile = KeyFile.from_keygenerator(keygen, sample_source_text)
        
        original = Encoder(keyfile.encode_map, keyfile.get_decode_map_int())
        mixed = keyfile.mix(shift=5)
        mixed_encoder = Encoder(mixed.encode_map, mixed.get_decode_map_int())
        
        text = "Hello, World! 12345"
        original_encoded = original.encode(text)
        mixed_encoded = mixed_encoder.encode(text)
        
        assert mixed_encoded != original_encoded
        assert mixed_encoder.decode(mixed_encoded) == text
        assert original.decode(original_encoded) == text
