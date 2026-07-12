"""
Tests for xenco.validator module.
"""

import pytest
from xenco.validator import (
    Validator, ValidationError, SourceError, KeyError, InputError,
    XencoError, validate_all
)


class TestValidatorAsciiRange:
    """Test ASCII range validation."""
    
    def test_valid_range(self):
        """Test valid ASCII ranges."""
        Validator.validate_ascii_range(32, 128)
        Validator.validate_ascii_range(0, 127)
        Validator.validate_ascii_range(40, 120)
    
    def test_invalid_types(self):
        """Test invalid types raise ValidationError."""
        with pytest.raises(ValidationError):
            Validator.validate_ascii_range("32", 128)
        with pytest.raises(ValidationError):
            Validator.validate_ascii_range(32, "128")
    
    def test_from_negative(self):
        """Test negative from value."""
        with pytest.raises(ValidationError) as exc_info:
            Validator.validate_ascii_range(-1, 100)
        assert "must be >= 0" in str(exc_info.value)
    
    def test_to_exceeds_max(self):
        """Test to value exceeding 127."""
        with pytest.raises(ValidationError) as exc_info:
            Validator.validate_ascii_range(0, 128)
        assert "must be <=" in str(exc_info.value)
    
    def test_from_greater_than_to(self):
        """Test from >= to."""
        with pytest.raises(ValidationError) as exc_info:
            Validator.validate_ascii_range(100, 50)
        assert "must be less than" in str(exc_info.value)
    
    def test_range_too_small(self):
        """Test range with fewer than 64 characters."""
        with pytest.raises(ValidationError) as exc_info:
            Validator.validate_ascii_range(32, 40)
        assert "too small" in str(exc_info.value)


class TestValidatorSource:
    """Test source validation."""
    
    def test_validate_source_content_sufficient(self):
        """Test content with sufficient unique characters."""
        content = "".join(chr(i) for i in range(32, 96))
        result = Validator.validate_source_content(content, 32, 128)
        assert len(result) >= 64
    
    def test_validate_source_content_insufficient(self):
        """Test content with insufficient unique characters."""
        with pytest.raises(SourceError) as exc_info:
            Validator.validate_source_content("abc", 32, 128)
        assert "only 4" in str(exc_info.value)
    
    def test_validate_source_content_empty(self):
        """Test empty content."""
        with pytest.raises(SourceError):
            Validator.validate_source_content("", 32, 128)
    
    def test_validate_source_type_url(self):
        """Test URL source type detection."""
        assert Validator.validate_source_type("http://example.com") == "url"
        assert Validator.validate_source_type("https://example.com") == "url"
    
    def test_validate_source_type_file(self, temp_dir):
        """Test file source type detection."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")
        assert Validator.validate_source_type(str(test_file)) == "file"
    
    def test_validate_source_type_text(self):
        """Test text source type detection."""
        assert Validator.validate_source_type("just some text") == "text"
    
    def test_validate_source_type_empty(self):
        """Test empty source."""
        with pytest.raises(SourceError):
            Validator.validate_source_type("")
    
    def test_validate_source_type_directory(self, temp_dir):
        """Test directory source raises error."""
        with pytest.raises(SourceError) as exc_info:
            Validator.validate_source_type(str(temp_dir))
        assert "not a file" in str(exc_info.value)


class TestValidatorKeyMappings:
    """Test key mapping validation."""
    
    def test_valid_mappings(self):
        """Test valid key mappings."""
        encode_map = {c: chr(32 + i) for i, c in enumerate(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
        )}
        decode_map = {ord(v): k for k, v in encode_map.items()}
        Validator.validate_key_mappings(encode_map, decode_map)
    
    def test_missing_base64_chars(self):
        """Test missing base64 characters."""
        encode_map = {"A": "!", "B": "@"}
        decode_map = {ord("!"): "A", ord("@"): "B"}
        
        with pytest.raises(KeyError) as exc_info:
            Validator.validate_key_mappings(encode_map, decode_map)
        assert "incomplete" in str(exc_info.value).lower()


class TestExceptionInheritance:
    """Test exception class inheritance."""
    
    def test_xenco_error_base(self):
        """Test XencoError is base."""
        assert issubclass(ValidationError, XencoError)
        assert issubclass(SourceError, XencoError)
        assert issubclass(KeyError, XencoError)
        assert issubclass(InputError, XencoError)
