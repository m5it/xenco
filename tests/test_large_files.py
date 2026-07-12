"""
Tests for large file handling.
"""

import pytest
from xenco.utils import read_file_chunked, write_file_chunked
from xenco.encoder import Encoder


class TestLargeFileHandling:
    """Test handling of large files."""
    
    def test_chunked_read(self, temp_dir):
        """Test chunked file reading."""
        # Create 100KB file
        test_file = temp_dir / "large.txt"
        content = "A" * (100 * 1024)  # 100KB
        test_file.write_text(content)
        
        # Read in chunks
        chunks = []
        for chunk in read_file_chunked(str(test_file), chunk_size=1024):
            chunks.append(chunk)
        
        # Verify
        result = "".join(chunks)
        assert len(result) == len(content)
        assert result == content
    
    def test_chunked_write(self, temp_dir):
        """Test chunked file writing."""
        output_file = temp_dir / "output.txt"
        
        # Create chunks
        chunks = ["chunk" + str(i) for i in range(100)]
        
        # Write in chunks
        total = write_file_chunked(str(output_file), iter(chunks))
        
        # Verify
        result = output_file.read_text()
        expected = "".join(chunks)
        assert result == expected
    
    def test_encode_large_data(self, mock_key_mappings, temp_dir):
        """Test encoding large data."""
        encode_map, decode_map = mock_key_mappings
        encoder = Encoder(encode_map, decode_map)
        
        # Create large text (100KB)
        large_text = "X" * (100 * 1024)
        
        # Encode
        encoded = encoder.encode(large_text)
        
        # Decode
        decoded = encoder.decode(encoded)
        
        assert decoded == large_text
    
    def test_encode_iter_large(self, mock_key_mappings, temp_dir):
        """Test iterative encoding of large data."""
        encode_map, decode_map = mock_key_mappings
        encoder = Encoder(encode_map, decode_map)
        
        # Large text
        large_text = "A" * 10000
        
        # Encode iteratively
        chunks = list(encoder.encode_iter(large_text, chunk_size=1000))
        
        # Full encode
        full_encoded = encoder.encode(large_text)
        
        # Should match
        assert "".join(chunks) == full_encoded
