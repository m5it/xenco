"""
Tests for xenco.keygen module.
"""

import pytest
from xenco.keygen import KeyGenerator, KeyGenerationError, InsufficientSourceError


class TestKeyGenerator:
    """Test KeyGenerator class."""
    
    def test_init_default_range(self):
        """Test initialization with default ASCII range."""
        kg = KeyGenerator()
        assert kg.ascii_from == 32
        assert kg.ascii_to == 128
    
    def test_init_custom_range(self):
        """Test initialization with custom ASCII range."""
        kg = KeyGenerator(ascii_from=40, ascii_to=100)
        assert kg.ascii_from == 40
        assert kg.ascii_to == 100
    
    def test_init_invalid_range(self):
        """Test initialization with invalid ranges raises ValueError."""
        # from >= to
        with pytest.raises(ValueError):
            KeyGenerator(ascii_from=100, ascii_to=50)
        
        # from < 0
        with pytest.raises(ValueError):
            KeyGenerator(ascii_from=-1, ascii_to=100)
        
        # to > 128
        with pytest.raises(ValueError):
            KeyGenerator(ascii_from=0, ascii_to=129)
    
    def test_is_url(self):
        """Test URL detection."""
        kg = KeyGenerator()
        assert kg._is_url("http://example.com") is True
        assert kg._is_url("https://example.com") is True
        assert kg._is_url("HTTPS://EXAMPLE.COM") is True
        assert kg._is_url("ftp://example.com") is False
        assert kg._is_url("/path/to/file") is False
        assert kg._is_url("just text") is False
    
    def test_extract_unique_chars(self):
        """Test unique character extraction."""
        kg = KeyGenerator(ascii_from=32, ascii_to=128)
        content = "abcabcabc xyz xyz 123 123"
        unique = kg._extract_unique_chars(content)
        
        # Should have unique chars in order of first appearance
        assert 'a' in unique
        assert 'b' in unique
        assert 'c' in unique
        assert ' ' in unique
        assert 'x' in unique
        assert 'y' in unique
        assert 'z' in unique
        assert '1' in unique
        assert '2' in unique
        assert '3' in unique
    
    def test_validate_sufficient_chars_pass(self):
        """Test validation passes with sufficient characters."""
        kg = KeyGenerator(32, 128)
        # Create content with 64+ unique chars
        content = "".join(chr(i) for i in range(32, 96))
        unique = kg._extract_unique_chars(content)
        # Should not raise
        kg._validate_sufficient_chars(unique)
    
    def test_validate_sufficient_chars_fail(self):
        """Test validation fails with insufficient characters."""
        kg = KeyGenerator(32, 128)
        content = "abc"  # Only 3 unique chars + space = 4
        unique = kg._extract_unique_chars(content)
        
        with pytest.raises(InsufficientSourceError) as exc_info:
            kg._validate_sufficient_chars(unique)
        
        assert "64" in str(exc_info.value)
        assert "only 4" in str(exc_info.value)
    
    def test_generate_from_text(self, sample_source_text):
        """Test key generation from text source."""
        kg = KeyGenerator(32, 128)
        encode_map, decode_map = kg.generate(sample_source_text)
        
        # Check we have 64 mappings
        assert len(encode_map) == 64
        assert len(decode_map) == 64
        
        # Check bidirectional consistency
        for b64_char, key_char in encode_map.items():
            key_code = ord(key_char)
            assert decode_map[key_code] == b64_char
    
    def test_generate_from_file(self, sample_source_file):
        """Test key generation from file source."""
        kg = KeyGenerator(32, 128)
        encode_map, decode_map = kg.generate(sample_source_file)
        
        assert len(encode_map) == 64
        assert len(decode_map) == 64
    
    def test_generate_insufficient_source(self):
        """Test generation fails with insufficient source."""
        kg = KeyGenerator(32, 128)
        with pytest.raises(InsufficientSourceError):
            kg.generate("abc")  # Not enough unique chars
    
    def test_get_key_info(self, sample_source_text):
        """Test getting key info."""
        kg = KeyGenerator(32, 128)
        info = kg.get_key_info(sample_source_text)
        
        assert info["source"] == sample_source_text
        assert info["is_url"] is False
        assert info["is_file"] is False
        assert info["ascii_range"] == "32-128"
        assert info["sufficient"] is True
        assert info["unique_chars"] >= 64
    
    def test_clear_cache(self, sample_source_text):
        """Test cache clearing."""
        kg = KeyGenerator(32, 128)
        kg.generate(sample_source_text)
        assert len(kg._content_cache) > 0
        
        kg.clear_cache()
        assert len(kg._content_cache) == 0
    
    def test_caching(self, sample_source_text):
        """Test that content is cached."""
        kg = KeyGenerator(32, 128)
        
        # First call should cache
        kg.generate(sample_source_text)
        cache_size = len(kg._content_cache)
        assert cache_size == 1
        
        # Second call should use cache
        kg.generate(sample_source_text)
        assert len(kg._content_cache) == cache_size


class TestKeyGenerationError:
    """Test KeyGenerationError exception."""
    
    def test_exception_inheritance(self):
        """Test that exceptions inherit from correct base."""
        assert issubclass(KeyGenerationError, Exception)
        assert issubclass(InsufficientSourceError, KeyGenerationError)
"""
Tests for xenco.keygen module.
"""

import pytest
from xenco.keygen import KeyGenerator, KeyGenerationError, InsufficientSourceError


class TestKeyGenerator:
    """Test KeyGenerator class."""
    
    def test_init_default_range(self):
        """Test initialization with default ASCII range."""
        kg = KeyGenerator()
        assert kg.ascii_from == 32
        assert kg.ascii_to == 128
    
    def test_init_custom_range(self):
        """Test initialization with custom ASCII range."""
        kg = KeyGenerator(ascii_from=40, ascii_to=100)
        assert kg.ascii_from == 40
        assert kg.ascii_to == 100
    
    def test_init_invalid_range(self):
        """Test initialization with invalid ranges raises ValueError."""
        # from >= to
        with pytest.raises(ValueError):
            KeyGenerator(ascii_from=100, ascii_to=50)
        
        # from < 0
        with pytest.raises(ValueError):
            KeyGenerator(ascii_from=-1, ascii_to=100)
        
        # to > 128
        with pytest.raises(ValueError):
            KeyGenerator(ascii_from=0, ascii_to=129)
    
    def test_is_url(self):
        """Test URL detection."""
        kg = KeyGenerator()
        assert kg._is_url("http://example.com") is True
        assert kg._is_url("https://example.com") is True
        assert kg._is_url("HTTPS://EXAMPLE.COM") is True
        assert kg._is_url("ftp://example.com") is False
        assert kg._is_url("/path/to/file") is False
        assert kg._is_url("just text") is False
    
    def test_extract_unique_chars(self):
        """Test unique character extraction."""
        kg = KeyGenerator(ascii_from=32, ascii_to=128)
        content = "abcabcabc xyz xyz 123 123"
        unique = kg._extract_unique_chars(content)
        
        # Should have unique chars in order of first appearance
        assert 'a' in unique
        assert 'b' in unique
        assert 'c' in unique
        assert ' ' in unique
        assert 'x' in unique
        assert 'y' in unique
        assert 'z' in unique
        assert '1' in unique
        assert '2' in unique
        assert '3' in unique
    
    def test_validate_sufficient_chars_pass(self):
        """Test validation passes with sufficient characters."""
        kg = KeyGenerator(32, 128)
        # Create content with 64+ unique chars
        content = "".join(chr(i) for i in range(32, 96))
        unique = kg._extract_unique_chars(content)
        # Should not raise
        kg._validate_sufficient_chars(unique)
    
    def test_validate_sufficient_chars_fail(self):
        """Test validation fails with insufficient characters."""
        kg = KeyGenerator(32, 128)
        content = "abc"  # Only 3 unique chars + space = 4
        unique = kg._extract_unique_chars(content)
        
        with pytest.raises(InsufficientSourceError) as exc_info:
            kg._validate_sufficient_chars(unique)
        
        assert "64" in str(exc_info.value)
        assert "only 4" in str(exc_info.value)
    
    def test_generate_from_text(self, sample_source_text):
        """Test key generation from text source."""
        kg = KeyGenerator(32, 128)
        encode_map, decode_map = kg.generate(sample_source_text)
        
        # Check we have 64 mappings
        assert len(encode_map) == 64
        assert len(decode_map) == 64
        
        # Check bidirectional consistency
        for b64_char, key_char in encode_map.items():
            key_code = ord(key_char)
            assert decode_map[key_code] == b64_char
    
    def test_generate_from_file(self, sample_source_file):
        """Test key generation from file source."""
        kg = KeyGenerator(32, 128)
        encode_map, decode_map = kg.generate(sample_source_file)
        
        assert len(encode_map) == 64
        assert len(decode_map) == 64
    
    def test_generate_insufficient_source(self):
        """Test generation fails with insufficient source."""
        kg = KeyGenerator(32, 128)
        with pytest.raises(InsufficientSourceError):
            kg.generate("abc")  # Not enough unique chars
    
    def test_get_key_info(self, sample_source_text):
        """Test getting key info."""
        kg = KeyGenerator(32, 128)
        info = kg.get_key_info(sample_source_text)
        
        assert info["source"] == sample_source_text
        assert info["is_url"] is False
        assert info["is_file"] is False
        assert info["ascii_range"] == "32-128"
        assert info["sufficient"] is True
        assert info["unique_chars"] >= 64
    
    def test_clear_cache(self, sample_source_text):
        """Test cache clearing."""
        kg = KeyGenerator(32, 128)
        kg.generate(sample_source_text)
        assert len(kg._content_cache) > 0
        
        kg.clear_cache()
        assert len(kg._content_cache) == 0
    
    def test_caching(self, sample_source_text):
        """Test that content is cached."""
        kg = KeyGenerator(32, 128)
        
        # First call should cache
        kg.generate(sample_source_text)
        cache_size = len(kg._content_cache)
        assert cache_size == 1
        
        # Second call should use cache
        kg.generate(sample_source_text)
        assert len(kg._content_cache) == cache_size



class TestGenerateKeyFunction:
    """Test generate_key() convenience function."""
    
    def test_generate_key_from_text(self, sample_source_text):
        """Test successful key generation from text source."""
        from xenco.keygen import generate_key
        
        # Generate without saving
        encode_map, decode_map = generate_key(sample_source_text)
        
        # Should return tuple of mappings
        assert isinstance(encode_map, dict)
        assert isinstance(decode_map, dict)
        assert len(encode_map) == 65  # 64 base64 + padding
        assert len(decode_map) == 65
        
        # Check bidirectional consistency
        for b64_char, key_char in encode_map.items():
            key_code = ord(key_char)
            assert decode_map[key_code] == b64_char
    
    def test_generate_key_with_output_file(self, sample_source_text, tmp_path):
        """Test key generation with output file saves correctly."""
        from xenco.keygen import generate_key
        from xenco.keyfile import KeyFile
        
        output_path = tmp_path / "test_key.xenco"
        
        # Generate with output path
        keyfile = generate_key(sample_source_text, output_path=str(output_path))
        
        # Should return KeyFile object
        assert isinstance(keyfile, KeyFile)
        
        # File should exist
        assert output_path.exists()
        
        # Should be loadable
        loaded = KeyFile.load(str(output_path))
        assert loaded.source == sample_source_text
        assert len(loaded.encode_map) == 65
    
    def test_generate_key_returns_mappings_without_output(self, sample_source_text):
        """Test that generate_key returns mappings when no output path."""
        from xenco.keygen import generate_key
        
        # Call without output_path
        result = generate_key(sample_source_text)
        
        # Should be a tuple
        assert isinstance(result, tuple)
        assert len(result) == 2
        
        encode_map, decode_map = result
        assert isinstance(encode_map, dict)
        assert isinstance(decode_map, dict)
    
    def test_generate_key_custom_ascii_range(self, sample_source_text):
        """Test generate_key with custom ASCII range."""
        from xenco.keygen import generate_key
        
        encode_map, decode_map = generate_key(
            sample_source_text,
            ascii_from=40,
            ascii_to=120
        )
        
        # Should still generate successfully
        assert len(encode_map) == 65
        assert len(decode_map) == 65
    
    def test_generate_key_insufficient_source(self):
        """Test generate_key raises InsufficientSourceError."""
        from xenco.keygen import generate_key, InsufficientSourceError
        
        with pytest.raises(InsufficientSourceError):
            generate_key("ABC")  # Only 3 unique chars, need 65
    
    def test_generate_key_pretty_print(self, sample_source_text, tmp_path):
        """Test generate_key with pretty=True creates readable JSON."""
        from xenco.keygen import generate_key
        
        output_path = tmp_path / "pretty_key.xenco"
        output_path_ugly = tmp_path / "ugly_key.xenco"
        
        # Generate pretty
        generate_key(sample_source_text, output_path=str(output_path), pretty=True)
        
        # Generate not pretty
        generate_key(sample_source_text, output_path=str(output_path_ugly), pretty=False)
        
        # Pretty file should be larger (more whitespace)
        pretty_size = output_path.stat().st_size
        ugly_size = output_path_ugly.stat().st_size
        assert pretty_size >= ugly_size
        
        # Pretty file should contain newlines
        pretty_content = output_path.read_text()
        assert '\n' in pretty_content
    
    def test_generate_key_default_parameters(self, sample_source_text):
        """Test generate_key uses correct defaults."""
        from xenco.keygen import generate_key
        
        # Call with only source
        result = generate_key(sample_source_text)
        
        # Should work with default ASCII range 32-127
        assert isinstance(result, tuple)
        encode_map, decode_map = result
        assert len(encode_map) == 65



class TestKeyGenerationError:
    """Test KeyGenerationError exception."""
    
    def test_exception_inheritance(self):
        """Test that exceptions inherit from correct base."""
        assert issubclass(KeyGenerationError, Exception)
        assert issubclass(InsufficientSourceError, KeyGenerationError)
