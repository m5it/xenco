"""
Tests for xenco.encoder module.
"""

import pytest
from xenco.encoder import Encoder, EncodingError, InvalidCharacterError


class TestEncoder:
    """Test Encoder class."""
    
    def test_init_valid_mappings(self, mock_key_mappings):
        """Test initialization with valid mappings."""
        encode_map, decode_map = mock_key_mappings
        encoder = Encoder(encode_map, decode_map)
        assert encoder.encode_map == encode_map
        assert encoder.decode_map == decode_map
    
    def test_init_invalid_mappings(self):
        """Test initialization with invalid mappings raises ValueError."""
        # Missing base64 characters
        incomplete_encode = {'A': '!', 'B': '@'}
        incomplete_decode = {ord('!'): 'A', ord('@'): 'B'}
        
        with pytest.raises(ValueError):
            Encoder(incomplete_encode, incomplete_decode)
    
    def test_encode_string(self, mock_key_mappings):
        """Test encoding a string."""
        encode_map, decode_map = mock_key_mappings
        encoder = Encoder(encode_map, decode_map)
        
        encoded = encoder.encode("Hello")
        assert isinstance(encoded, str)
        assert len(encoded) > 0
    
    def test_encode_bytes(self, mock_key_mappings):
        """Test encoding bytes."""
        encode_map, decode_map = mock_key_mappings
        encoder = Encoder(encode_map, decode_map)
        
        encoded = encoder.encode(b"Hello")
        assert isinstance(encoded, str)
    
    def test_encode_return_bytes(self, mock_key_mappings):
        """Test encoding with return_bytes=True."""
        encode_map, decode_map = mock_key_mappings
        encoder = Encoder(encode_map, decode_map)
        
        encoded = encoder.encode("Hello", return_bytes=True)
        assert isinstance(encoded, bytes)
    
    def test_decode_string(self, mock_key_mappings):
        """Test decoding a string."""
        encode_map, decode_map = mock_key_mappings
        encoder = Encoder(encode_map, decode_map)
        
        original = "Hello, World! 123"
        encoded = encoder.encode(original)
        decoded = encoder.decode(encoded)
        
        assert decoded == original
    
    def test_decode_bytes(self, mock_key_mappings):
        """Test decoding bytes."""
        encode_map, decode_map = mock_key_mappings
        encoder = Encoder(encode_map, decode_map)
        
        original = "Test message"
        encoded = encoder.encode(original)
        encoded_bytes = encoded.encode('utf-8')
        
        decoded = encoder.decode(encoded_bytes)
        assert decoded == original
    
    def test_roundtrip_various_strings(self, mock_key_mappings):
        """Test roundtrip encoding/decoding with various strings."""
        encode_map, decode_map = mock_key_mappings
        encoder = Encoder(encode_map, decode_map)
        
        test_strings = [
            "Hello, World!",
            "The quick brown fox jumps over the lazy dog.",
            "1234567890",
            "!@#$%^&*()",
            "Unicode: café résumé",
            "",  # Empty string
            "A" * 1000,  # Long string
        ]
        
        for text in test_strings:
            encoded = encoder.encode(text)
            decoded = encoder.decode(encoded)
            assert decoded == text, f"Failed for: {text[:50]}..."
    
    def test_verify_roundtrip(self, mock_key_mappings):
        """Test verify_roundtrip method."""
        encode_map, decode_map = mock_key_mappings
        encoder = Encoder(encode_map, decode_map)
        
        assert encoder.verify_roundtrip("Test data") is True
    
    def test_from_keygenerator(self, sample_source_text):
        """Test creating encoder from KeyGenerator."""
        from xenco.keygen import KeyGenerator
        
        keygen = KeyGenerator(32, 128)
        encoder = Encoder.from_keygenerator(keygen, sample_source_text)
        
        assert isinstance(encoder, Encoder)
        assert len(encoder.encode_map) == 64


class TestEncodingErrors:
    """Test encoding error handling."""
    
    def test_invalid_character_error(self):
        """Test InvalidCharacterError."""
        err = InvalidCharacterError("Test error")
        assert isinstance(err, EncodingError)
        assert "Test error" in str(err)
    
    def test_decode_invalid_character(self, mock_key_mappings):
        """Test decoding with invalid character."""
        encode_map, decode_map = mock_key_mappings
        encoder = Encoder(encode_map, decode_map)
        
        # Create encoded text with invalid character
        invalid_text = "~~~"  # Characters not in decode_map
        
        with pytest.raises(InvalidCharacterError):
            encoder.decode(invalid_text)


class TestStreamOperations:
    """Test streaming operations."""
    
    def test_encode_stream(self, mock_key_mappings, temp_dir):
        """Test encode_stream method."""
        encode_map, decode_map = mock_key_mappings
        encoder = Encoder(encode_map, decode_map)
        
        # Create input file
        input_path = temp_dir / "input.txt"
        input_path.write_text("Hello, World!")
        
        # Create output file
        output_path = temp_dir / "output.txt"
        
        with open(input_path, "rb") as infile:
            with open(output_path, "w") as outfile:
                bytes_written = encoder.encode_stream(infile, outfile)
        
        assert bytes_written > 0
        assert output_path.exists()
    
    def test_decode_stream(self, mock_key_mappings, temp_dir):
        """Test decode_stream method."""
        encode_map, decode_map = mock_key_mappings
        encoder = Encoder(encode_map, decode_map)
        
        # Create encoded file
        original = "Test message for streaming"
        encoded = encoder.encode(original)
        
        input_path = temp_dir / "encoded.txt"
        input_path.write_text(encoded)
        
        output_path = temp_dir / "decoded.txt"
        
        with open(input_path, "r") as infile:
            with open(output_path, "w") as outfile:
                bytes_written = encoder.decode_stream(infile, outfile)
        
        assert bytes_written > 0
        assert output_path.read_text().strip() == original


class TestIterOperations:
    """Test iterative operations."""
    
    def test_encode_iter(self, mock_key_mappings):
        """Test encode_iter method."""
        encode_map, decode_map = mock_key_mappings
        encoder = Encoder(encode_map, decode_map)
        
        text = "Hello, World! This is a test."
        chunks = list(encoder.encode_iter(text, chunk_size=10))
        
        assert len(chunks) > 0
        # Full encoding should equal concatenated chunks
        full_encode = encoder.encode(text)
        assert "".join(chunks) == full_encode
    
    def test_decode_iter(self, mock_key_mappings):
        """Test decode_iter method."""
        encode_map, decode_map = mock_key_mappings
        encoder = Encoder(encode_map, decode_map)
        
        original = "Testing iterative decoding"
        encoded = encoder.encode(original)
        
        chunks = list(encoder.decode_iter(encoded, chunk_size=5))
        
        assert len(chunks) > 0
        assert "".join(chunks) == original
