"""
xEnco Encoding/Decoding Engine

Core encoding and decoding functionality using key-based character mapping.
"""

import base64
import io
from typing import Dict, Iterator, Optional, Union


class EncodingError(Exception):
    """Exception raised when encoding/decoding fails."""
    pass


class InvalidCharacterError(EncodingError):
    """Exception raised when invalid character encountered."""
    pass


class Encoder:
    """
    Encoder/decoder for text using key-based character mapping.
    
    Encoding process:
    1. Convert text to bytes (UTF-8)
    2. Base64 encode
    3. Map each base64 char to key character
    
    Decoding process:
    1. Map each encoded char back to base64 char
    2. Base64 decode
    3. Convert bytes to text (UTF-8)
    
    Attributes:
        encode_map (dict): Maps base64 chars to key chars
        decode_map (dict): Maps key char ASCII codes to base64 chars
    """
    
    def __init__(self, encode_map: Dict[str, str], decode_map: Dict[int, str]):
        """
        Initialize Encoder with key mappings.
        
        Args:
            encode_map: Dict mapping base64 chars to key chars
            decode_map: Dict mapping key char ASCII codes to base64 chars
        
        Raises:
            ValueError: If mappings are invalid
        """
        self.encode_map = encode_map
        self.decode_map = decode_map
        
        # Validate mappings
        self._validate_mappings()
    
    def _validate_mappings(self) -> None:
        """Validate that key mappings are complete and consistent."""
        required_b64 = (
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "abcdefghijklmnopqrstuvwxyz"
            "0123456789"
            "+/="
        )
        
        # Check encode_map has all base64 chars (including padding)
        missing = set(required_b64) - set(self.encode_map.keys())
        if missing:
            raise ValueError(f"encode_map missing base64 chars: {missing}")
        
        # Check decode_map has corresponding entries
        for b64_char, key_char in self.encode_map.items():
            key_code = ord(key_char)
            if key_code not in self.decode_map:
                raise ValueError(f"decode_map missing entry for key char '{key_char}'")
            if self.decode_map[key_code] != b64_char:
                raise ValueError(f"decode_map inconsistent at code {key_code}")
    
    def encode(
        self,
        data: Union[str, bytes],
        return_bytes: bool = False
    ) -> Union[str, bytes]:
        """
        Encode data using key mapping.
        
        Args:
            data: Text string or bytes to encode
            return_bytes: If True, return bytes; if False, return string
        
        Returns:
            Encoded data as string or bytes
        
        Raises:
            EncodingError: If encoding fails
        """
        try:
            # Convert to bytes if string
            if isinstance(data, str):
                data_bytes = data.encode("utf-8")
            else:
                data_bytes = data
            
            # Base64 encode
            b64_bytes = base64.b64encode(data_bytes)
            b64_str = b64_bytes.decode("ascii")
            
            # Map to key characters
            encoded_chars = []
            for char in b64_str:
                if char not in self.encode_map:
                    raise InvalidCharacterError(f"Unexpected base64 char: {char}")
                encoded_chars.append(self.encode_map[char])
            
            result = "".join(encoded_chars)
            
            if return_bytes:
                return result.encode("utf-8")
            return result
            
        except Exception as e:
            if isinstance(e, EncodingError):
                raise
            raise EncodingError(f"Encoding failed: {e}")
    
    def decode(
        self,
        data: Union[str, bytes],
        return_bytes: bool = False
    ) -> Union[str, bytes]:
        """
        Decode data using key mapping.
        
        Args:
            data: Encoded string or bytes to decode
            return_bytes: If True, return bytes; if False, return string
        
        Returns:
            Decoded data as string or bytes
        
        Raises:
            EncodingError: If decoding fails
            InvalidCharacterError: If encoded data contains invalid characters
        """
        try:
            # Convert to string if bytes
            if isinstance(data, bytes):
                data_str = data.decode("utf-8")
            else:
                data_str = data
            
            # Map back to base64
            b64_chars = []
            for char in data_str:
                char_code = ord(char)
                if char_code not in self.decode_map:
                    raise InvalidCharacterError(
                        f"Invalid encoded char '{char}' (code {char_code})"
                    )
                b64_chars.append(self.decode_map[char_code])
            
            b64_str = "".join(b64_chars)
            
            # Base64 decode
            decoded_bytes = base64.b64decode(b64_str)
            
            if return_bytes:
                return decoded_bytes
            return decoded_bytes.decode("utf-8")
            
        except Exception as e:
            if isinstance(e, EncodingError):
                raise
            raise EncodingError(f"Decoding failed: {e}")
    
    def encode_stream(
        self,
        input_stream: io.IOBase,
        output_stream: io.IOBase,
        chunk_size: int = 8192
    ) -> int:
        """
        Encode data from input stream to output stream.
        
        For large files, reads input in chunks, buffers until complete
        base64 chunks available, then encodes and writes.
        
        Args:
            input_stream: Readable stream
            output_stream: Writable stream
            chunk_size: Size of chunks to read
        
        Returns:
            Number of bytes written
        
        Raises:
            EncodingError: If encoding fails
        """
        bytes_written = 0
        buffer = b""
        
        try:
            while True:
                chunk = input_stream.read(chunk_size)
                if not chunk:
                    break
                buffer += chunk
            
            # Encode complete buffer
            encoded = self.encode(buffer, return_bytes=True)
            output_stream.write(encoded)
            bytes_written = len(encoded)
            
        except Exception as e:
            if isinstance(e, EncodingError):
                raise
            raise EncodingError(f"Stream encoding failed: {e}")
        
        return bytes_written
    
    def decode_stream(
        self,
        input_stream: io.IOBase,
        output_stream: io.IOBase,
        chunk_size: int = 8192
    ) -> int:
        """
        Decode data from input stream to output stream.
        
        Args:
            input_stream: Readable stream
            output_stream: Writable stream
            chunk_size: Size of chunks to read
        
        Returns:
            Number of bytes written
        
        Raises:
            EncodingError: If decoding fails
        """
        bytes_written = 0
        buffer = ""
        
        try:
            while True:
                chunk = input_stream.read(chunk_size)
                if not chunk:
                    break
                # Handle both string and bytes
                if isinstance(chunk, bytes):
                    buffer += chunk.decode("utf-8")
                else:
                    buffer += chunk
            
            # Decode complete buffer
            decoded = self.decode(buffer, return_bytes=True)
            output_stream.write(decoded)
            bytes_written = len(decoded)
            
        except Exception as e:
            if isinstance(e, EncodingError):
                raise
            raise EncodingError(f"Stream decoding failed: {e}")
        
        return bytes_written
    
    def encode_iter(
        self,
        data: str,
        chunk_size: int = 1024
    ) -> Iterator[str]:
        """
        Encode data iteratively, yielding chunks.
        
        Useful for large data that shouldn't be fully loaded in memory.
        
        Args:
            data: Text to encode
            chunk_size: Size of base64 chunks to process
        
        Yields:
            Encoded text chunks
        """
        # Process in chunks to avoid memory issues with huge data
        total_len = len(data)
        
        for i in range(0, total_len, chunk_size):
            chunk = data[i:i + chunk_size]
            encoded_chunk = self.encode(chunk)
            yield encoded_chunk
    
    def decode_iter(
        self,
        data: str,
        chunk_size: int = 1024
    ) -> Iterator[str]:
        """
        Decode data iteratively, yielding chunks.
        
        Args:
            data: Encoded text to decode
            chunk_size: Size of chunks to process
        
        Yields:
            Decoded text chunks
        """
        total_len = len(data)
        
        for i in range(0, total_len, chunk_size):
            chunk = data[i:i + chunk_size]
            decoded_chunk = self.decode(chunk)
            yield decoded_chunk
    
    def verify_roundtrip(self, test_data: str = "Hello, World! 123") -> bool:
        """
        Verify that encode/decode roundtrip works correctly.
        
        Args:
            test_data: Test string to use
        
        Returns:
            True if roundtrip successful, False otherwise
        """
        try:
            encoded = self.encode(test_data)
            decoded = self.decode(encoded)
            return decoded == test_data
        except Exception:
            return False
    
    @classmethod
    def from_keygenerator(cls, keygen, source: str):
        """
        Create Encoder directly from KeyGenerator and source.
        
        Args:
            keygen: KeyGenerator instance
            source: Source to generate key from
        
        Returns:
            Encoder instance
        """
        encode_map, decode_map = keygen.generate(source)
        return cls(encode_map, decode_map)
