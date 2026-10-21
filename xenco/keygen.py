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
        if not (0 < ascii_to <= 127):
            raise ValueError(f"ascii_to must be 1-127, got {ascii_to}")
        if ascii_to - ascii_from + 1 < len(self.BASE64_CHARS):
            raise ValueError(
                f"ASCII range must contain at least {len(self.BASE64_CHARS)} "
                f"characters, got {ascii_to - ascii_from + 1}"
            )
        if ascii_from >= ascii_to:
            raise ValueError(f"ascii_from ({ascii_from}) must be < ascii_to ({ascii_to})")
        
        self.ascii_from = ascii_from
        self.ascii_to = ascii_to
        self._content_cache: Dict[str, str] = {}
    
    def _is_url(self, source: str) -> bool:
        """Check if source is a URL."""
        return bool(re.match(r"^https?://", source, re.IGNORECASE))

    def _is_directory(self, source: str) -> bool:
        """Check if source is a directory path."""
        return os.path.isdir(source)
    
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
    
    def _read_directory(self, path: str) -> str:
        """
        Read concatenated content from all text files in a directory.

        Files that fail to decode as UTF-8 are skipped. Binary files and
        very common non-text entries are ignored.

        Args:
            path: Directory path

        Returns:
            Concatenated content of all readable text files

        Raises:
            KeyGenerationError: If directory cannot be read
        """
        try:
            entries = sorted(os.listdir(path))
        except Exception as e:
            raise KeyGenerationError(f"Failed to read directory {path}: {e}")

        # File extensions commonly considered text / encodable
        text_extensions = {
            ".txt", ".md", ".py", ".js", ".html", ".htm", ".css",
            ".json", ".xml", ".yaml", ".yml", ".ini", ".cfg", ".conf",
            ".log", ".csv", ".tsv", ".sh", ".bash", ".zsh", ".c",
            ".cpp", ".h", ".hpp", ".java", ".go", ".rs", ".rb",
            ".php", ".pl", ".pm", ".lua", ".sql", ".swift", ".kt",
            ".scala", ".r", ".m", ".matlab", ".tex", ".bib", "",
        }

        parts = []
        for entry in entries:
            filepath = os.path.join(path, entry)
            if not os.path.isfile(filepath):
                continue

            # Skip known non-text files by extension
            ext = os.path.splitext(entry)[1].lower()
            if ext and ext not in text_extensions:
                continue

            try:
                with open(filepath, "r", encoding="utf-8", errors="strict") as f:
                    parts.append(f.read())
            except UnicodeDecodeError:
                # Treat as binary / non-text, skip silently
                continue
            except Exception:
                continue

        return "\n".join(parts)

    def _get_content(self, source: str) -> str:
        """
        Get content from source with caching.
        
        Args:
            source: URL, file path, directory path, or raw text
        
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
        elif self._is_directory(source):
            content = self._read_directory(source)
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
    
    def _ensure_charset_coverage(
        self,
        source: str,
        unique_chars: list,
        encode_map: Dict[str, str],
        decode_map: Dict[int, str]
    ) -> Tuple[list, Dict[str, str], Dict[int, str]]:
        """
        Ensure the generated key can encode every character found in the source.

        This is primarily useful when the source is a directory. If a source
        character is not already used in the 65 base64 mappings, the method
        attempts to assign it to a mapping slot that uses a character which is
        also present elsewhere in the source (i.e. replaceable without loss of
        coverage). When this is not possible, the key will still work for any
        text, but the source directory may contain characters that the key was
        not built around.

        Args:
            source: Original source identifier
            unique_chars: Unique characters already extracted from source
            encode_map: Current base64 -> source character mapping
            decode_map: Current source code -> base64 mapping

        Returns:
            Tuple of (unique_chars, encode_map, decode_map)
        """
        content = self._get_content(source)
        source_chars = set(content)
        mapped_chars = set(encode_map.values())
        missing = source_chars - mapped_chars

        if not missing:
            return unique_chars, encode_map, decode_map

        # Try to swap each missing character into the mapping if we can free
        # a currently mapped character that still appears elsewhere.
        for missing_char in sorted(missing, key=ord):
            if missing_char in mapped_chars:
                continue

            # Find a base64 slot whose current character appears at least twice
            # in the original content, so removing one occurrence still leaves
            # that character available if needed later.
            base64_chars = list(encode_map.keys())
            for b64_char in base64_chars:
                current_char = encode_map[b64_char]
                if content.count(current_char) > 1:
                    # Replace with the missing character
                    encode_map[b64_char] = missing_char
                    del decode_map[ord(current_char)]
                    decode_map[ord(missing_char)] = b64_char
                    mapped_chars.discard(current_char)
                    mapped_chars.add(missing_char)
                    break
            else:
                # No swappable slot found; we keep the current mapping
                pass

        return unique_chars, encode_map, decode_map

    def generate(self, source: str) -> Tuple[Dict[str, str], Dict[int, str]]:
        """
        Generate key mapping from source.
        
        Creates two mappings:
        - encode_map: base64_char -> source_char (for encoding)
        - decode_map: ascii_code -> base64_char (for decoding)
        
        Args:
            source: URL, file path, directory path, or raw text to generate key from
        
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
        
        # If source is a directory, try to ensure all of its characters are
        # represented in the key mappings.
        if self._is_directory(source):
            unique_chars, encode_map, decode_map = self._ensure_charset_coverage(
                source, unique_chars, encode_map, decode_map
            )
        
        return encode_map, decode_map
    
    def get_key_info(self, source: str) -> dict:
        """
        Get information about a potential key source without generating.
        
        Args:
            source: URL, file path, directory path, or raw text
        
        Returns:
            Dictionary with source info
        """
        content = self._get_content(source)
        unique_chars = self._extract_unique_chars(content)
        
        source_type = "raw text"
        if self._is_url(source):
            source_type = "url"
        elif self._is_directory(source):
            source_type = "directory"
        elif os.path.exists(source):
            source_type = "file"
        
        return {
            "source": source,
            "source_type": source_type,
            "is_url": self._is_url(source),
            "is_directory": self._is_directory(source),
            "is_file": os.path.exists(source) and os.path.isfile(source),
            "ascii_range": f"{self.ascii_from}-{self.ascii_to}",
            "total_chars": len(content),
            "unique_chars": len(unique_chars),
            "sufficient": len(unique_chars) >= len(self.BASE64_CHARS),
            "sample_chars": unique_chars[:20] if unique_chars else []
        }
    
    def clear_cache(self) -> None:
        """Clear the content cache."""
        self._content_cache.clear()


def generate_key(
    source: str,
    output_path: Optional[str] = None,
    ascii_from: int = 32,
    ascii_to: int = 127,
    pretty: bool = False
):
    """
    Generate a key from a source with optional file output.
    
    This is a convenience function that wraps KeyGenerator and KeyFile
    for simple use cases. For advanced usage, use KeyGenerator directly.
    
    Args:
        source: URL, file path, or raw text to generate key from
        output_path: Optional path to save key file (.xenco extension)
        ascii_from: Starting ASCII code (default: 32)
        ascii_to: Ending ASCII code (default: 127)
        pretty: Pretty-print JSON output if saving to file
    
    Returns:
        If output_path is provided: KeyFile object
        If output_path is None: Tuple of (encode_map, decode_map)
    
    Raises:
        InsufficientSourceError: If source doesn't have enough unique characters
        KeyGenerationError: If source cannot be loaded or file cannot be written
    
    Examples:
        # Generate and save key from URL
        >>> keyfile = generate_key("https://example.com", "mykey.xenco")
        
        # Generate with custom ASCII range
        >>> keyfile = generate_key("source.txt", "key.xenco", ascii_from=40, ascii_to=120)
        
        # Generate without saving (returns mappings)
        >>> encode_map, decode_map = generate_key("my source text")
        
        # Generate with pretty-printed output
        >>> keyfile = generate_key("https://example.com", "key.xenco", pretty=True)
    """
    from .keyfile import KeyFile
    
    # Create generator and generate key
    keygen = KeyGenerator(ascii_from=ascii_from, ascii_to=ascii_to)
    encode_map, decode_map = keygen.generate(source)
    
    # If output path provided, save to file
    if output_path:
        keyfile = KeyFile(
            encode_map=encode_map,
            decode_map=decode_map,
            source=source,
            ascii_from=ascii_from,
            ascii_to=ascii_to
        )
        keyfile.save(output_path, pretty=pretty)
        return keyfile
    
    # Otherwise return the mappings
    return encode_map, decode_map
