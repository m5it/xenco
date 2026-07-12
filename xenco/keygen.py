"""
xEnco Key Generation

Generate encryption keys from URLs, files, or text data sources.
"""

import re
import os
import hashlib
from typing import Dict, Optional, Tuple, Union


class KeyGenerationError(Exception):
    """Exception raised when key generation fails."""
    pass


class InsufficientSourceError(KeyGenerationError):
    """Exception raised when source doesn't have enough unique characters."""
    pass


class KeyGenerator:
    """
    Generate encoding keys from data sources (URLs, files, or text).
    
    A key maps base64 characters (64 chars + padding) to unique characters from the source.
    """
    
    # Base64 characters that need mapping (64 chars + padding)
    BASE64_CHARS = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz"
        "0123456789"
        "+/="
    )
    
    def __init__(self, ascii_from: int = 32, ascii_to: int = 127):
        """
        Initialize KeyGenerator with ASCII range.
        
        Args:
            ascii_from: Starting ASCII code (inclusive), default 32 (space)
            ascii_to: Ending ASCII code (inclusive), default 127
        
        Raises:
            ValueError: If ascii_from >= ascii_to or out of valid range
        """
        if not (0 <= ascii_from < 128):
            raise ValueError(f"ascii_from must be 0-127, got {ascii_from}")
        if not (0 < ascii_to <= 128):
            raise ValueError(f"ascii_to must be 1-128, got {ascii_to}")
        if ascii_from >= ascii_to:
            raise ValueError(f"ascii_from ({ascii_from}) must be < ascii_to ({ascii_to})")
        
        self.ascii_from = ascii_from
        self.ascii_to = ascii_to
        self._content_cache: Dict[str, str] = {}
    
    def _is_url(self, source: str) -> bool:
        """Check if source is a URL."""
        return bool(re.match(r"^https?://", source, re.IGNORECASE))
    
    def _fetch_url(self, url: str) -> str:
        """
        Fetch content from URL.
        
        Args:
            url: URL to fetch
        
        Returns:
            Content as string
        
        Raises:
            KeyGenerationError: If request fails
        """
        try:
            import requests
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36"
                )
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except ImportError:
            raise KeyGenerationError("requests library required for URL sources")
        except Exception as e:
            raise KeyGenerationError(f"Failed to fetch URL {url}: {e}")
    
    def _read_file(self, path: str) -> str:
        """
        Read content from file.
        
        Args:
            path: File path
        
        Returns:
            Content as string
        
        Raises:
            KeyGenerationError: If file cannot be read
        """
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            raise KeyGenerationError(f"Failed to read file {path}: {e}")
    
    def _get_content(self, source: str) -> str:
        """
        Get content from source with caching.
        
        Args:
            source: URL, file path, or raw text
        
        Returns:
            Content as string
        """
        # Check cache first
        cache_key = hashlib.md5(source.encode()).hexdigest()
        if cache_key in self._content_cache:
            return self._content_cache[cache_key]
        
        # Load content
        if self._is_url(source):
            content = self._fetch_url(source)
        elif os.path.exists(source):
            content = self._read_file(source)
        else:
            # Treat as raw text
            content = source
        
        # Cache and return
        self._content_cache[cache_key] = content
        return content
    
    def _extract_unique_chars(self, content: str) -> list:
        """
        Extract unique characters from content within ASCII range.
        
        Args:
            content: Source content
        
        Returns:
            List of unique characters in order of first appearance
        """
        seen = set()
        unique_chars = []
        
        for char in content:
            code = ord(char)
            if (self.ascii_from <= code <= self.ascii_to and 
                char not in seen):
                seen.add(char)
                unique_chars.append(char)
        
        return unique_chars
    
    def _validate_sufficient_chars(self, unique_chars: list) -> None:
        """
        Validate source has enough unique characters.
        
        Args:
            unique_chars: List of unique characters
        
        Raises:
            InsufficientSourceError: If less than 65 unique characters (64 + padding)
        """
        count = len(unique_chars)
        required = len(self.BASE64_CHARS)  # 65 chars (64 + padding)
        if count < required:
            raise InsufficientSourceError(
                f"Source contains only {count} unique characters in range "
                f"[{self.ascii_from}-{self.ascii_to}], but {required} are required "
                f"for base64 encoding. Need {required - count} more unique characters."
            )
    
    def generate(self, source: str) -> Tuple[Dict[str, str], Dict[int, str]]:
        """
        Generate key mapping from source.
        
        Creates two mappings:
        - encode_map: base64_char -> source_char (for encoding)
        - decode_map: ascii_code -> base64_char (for decoding)
        
        Args:
            source: URL, file path, or raw text to generate key from
        
        Returns:
            Tuple of (encode_map, decode_map)
        
        Raises:
            InsufficientSourceError: If source doesn't have 65+ unique chars
            KeyGenerationError: If source cannot be loaded
        """
        # Get content
        content = self._get_content(source)
        
        # Extract unique characters
        unique_chars = self._extract_unique_chars(content)
        
        # Validate
        self._validate_sufficient_chars(unique_chars)
        
        # Create mappings
        encode_map = {}  # base64_char -> source_char
        decode_map = {}  # ascii_code -> base64_char
        
        for i, b64_char in enumerate(self.BASE64_CHARS):
            source_char = unique_chars[i]
            encode_map[b64_char] = source_char
            decode_map[ord(source_char)] = b64_char
        
        return encode_map, decode_map
    
    def get_key_info(self, source: str) -> dict:
        """
        Get information about a potential key source without generating.
        
        Args:
            source: URL, file path, or raw text
        
        Returns:
            Dictionary with source info
        """
        content = self._get_content(source)
        unique_chars = self._extract_unique_chars(content)
        
        return {
            "source": source,
            "is_url": self._is_url(source),
            "is_file": os.path.exists(source),
            "ascii_range": f"{self.ascii_from}-{self.ascii_to}",
            "total_chars": len(content),
            "unique_chars": len(unique_chars),
            "sufficient": len(unique_chars) >= len(self.BASE64_CHARS),
            "sample_chars": unique_chars[:20] if unique_chars else []
        }
    
    def clear_cache(self) -> None:
        """Clear the content cache."""
        self._content_cache.clear()
