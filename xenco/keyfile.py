"""
xEnco Key File Format

Save and load key files with metadata in JSON format.
"""

import json
import hashlib
import os
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class KeyFileError(Exception):
    """Exception raised for key file operations."""
    pass


class KeyFileCorruptedError(KeyFileError):
    """Exception raised when key file is corrupted or tampered."""
    pass


class KeyFileVersionError(KeyFileError):
    """Exception raised when key file version is incompatible."""
    pass


class KeyFile:
    """
    Handle key file persistence in JSON format.
    
    Key file format (version 1.0.0):
    {
        "version": "1.0.0",
        "created": "2024-01-15T10:30:00",
        "source": "https://example.com/page.html",
        "ascii_range": {"from": 32, "to": 128},
        "checksum": "sha256:abc123...",
        "encode_map": {"A": "!", "B": "@", ...},
        "decode_map": {"33": "A", "64": "B", ...}
    }
    
    Attributes:
        version (str): Key file format version
        encode_map (dict): Mapping for encoding
        decode_map (dict): Mapping for decoding
        metadata (dict): Additional metadata
    """
    
    CURRENT_VERSION = "1.0.0"
    SUPPORTED_VERSIONS = ["1.0.0"]
    
    def __init__(
        self,
        encode_map: Dict[str, str],
        decode_map: Dict[int, str],
        source: str,
        ascii_from: int,
        ascii_to: int,
        created: Optional[str] = None
    ):
        """
        Initialize KeyFile with key data.
        
        Args:
            encode_map: Dict mapping base64 chars to key chars
            decode_map: Dict mapping key char codes to base64 chars
            source: Original source of the key
            ascii_from: ASCII range start
            ascii_to: ASCII range end
            created: ISO format timestamp (auto-generated if None)
        """
        self.version = self.CURRENT_VERSION
        self.encode_map = encode_map
        self.decode_map = {str(k): v for k, v in decode_map.items()}  # JSON keys must be strings
        self.source = source
        self.ascii_from = ascii_from
        self.ascii_to = ascii_to
        self.created = created or datetime.now().isoformat()
        self._checksum: Optional[str] = None
    
    def _calculate_checksum(self) -> str:
        """
        Calculate SHA256 checksum of key data.
        
        Returns:
            Checksum string in format "sha256:hexdigest"
        """
        data = {
            "version": self.version,
            "encode_map": self.encode_map,
            "decode_map": self.decode_map,
            "source": self.source,
            "ascii_from": self.ascii_from,
            "ascii_to": self.ascii_to,
            "created": self.created
        }
        # Sort keys for consistent hashing
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        hash_obj = hashlib.sha256(json_str.encode('utf-8'))
        return f"sha256:{hash_obj.hexdigest()}"
    
    def to_dict(self) -> dict:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary with all key data and metadata
        """
        return {
            "version": self.version,
            "created": self.created,
            "source": self.source,
            "ascii_range": {
                "from": self.ascii_from,
                "to": self.ascii_to
            },
            "checksum": self._calculate_checksum(),
            "encode_map": self.encode_map,
            "decode_map": self.decode_map
        }
    
    def save(self, filepath: str, pretty: bool = False) -> None:
        """
        Save key file to disk.
        
        Args:
            filepath: Path to save key file
            pretty: If True, format with indentation for readability
        
        Raises:
            KeyFileError: If save fails
        """
        try:
            data = self.to_dict()
            self._checksum = data["checksum"]  # Store calculated checksum
            
            mode = 'w'
            kwargs = {}
            if pretty:
                kwargs['indent'] = 2
            else:
                kwargs['separators'] = (',', ':')
            
            with open(filepath, mode, encoding='utf-8') as f:
                json.dump(data, f, **kwargs)
                f.write('\n')
                
        except Exception as e:
            raise KeyFileError(f"Failed to save key file: {e}")
    
    @classmethod
    def load(cls, filepath: str, verify: bool = True) -> "KeyFile":
        """
        Load key file from disk.
        
        Args:
            filepath: Path to key file
            verify: If True, verify checksum integrity
        
        Returns:
            KeyFile instance
        
        Raises:
            KeyFileError: If load fails
            KeyFileCorruptedError: If checksum verification fails
            KeyFileVersionError: If version is incompatible
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise KeyFileError(f"Failed to load key file: {e}")
        
        # Check version compatibility
        version = data.get("version", "unknown")
        if version not in cls.SUPPORTED_VERSIONS:
            raise KeyFileVersionError(
                f"Key file version {version} not supported. "
                f"Supported versions: {cls.SUPPORTED_VERSIONS}"
            )

        # Validate required fields
        required_fields = ["encode_map", "decode_map", "source", "ascii_range"]
        missing = [field for field in required_fields if field not in data]
        if missing:
            raise KeyFileError(
                f"Key file missing required fields: {', '.join(missing)}"
            )
        if not all(k in data["ascii_range"] for k in ("from", "to")):
            raise KeyFileError(
                "Key file missing ascii_range 'from' or 'to' value"
            )

        # Verify checksum if present and requested
        if verify and "checksum" in data:
            stored_checksum = data["checksum"]
            # Create temporary instance to calculate expected checksum
            temp = cls(
                encode_map=data["encode_map"],
                decode_map={int(k): v for k, v in data["decode_map"].items()},
                source=data["source"],
                ascii_from=data["ascii_range"]["from"],
                ascii_to=data["ascii_range"]["to"],
                created=data["created"]
            )
            expected_checksum = temp._calculate_checksum()
            
            if stored_checksum != expected_checksum:
                raise KeyFileCorruptedError(
                    f"Key file checksum mismatch. File may be corrupted "
                    f"or tampered with."
                )
        
        # Convert decode_map keys back to integers
        decode_map = {int(k): v for k, v in data["decode_map"].items()}
        
        # Create instance
        keyfile = cls(
            encode_map=data["encode_map"],
            decode_map=decode_map,
            source=data["source"],
            ascii_from=data["ascii_range"]["from"],
            ascii_to=data["ascii_range"]["to"],
            created=data.get("created")
        )
        keyfile._checksum = data.get("checksum")
        
        return keyfile
    
    def get_decode_map_int(self) -> Dict[int, str]:
        """
        Get decode map with integer keys.
        
        Returns:
            Dict with integer keys (for use with Encoder)
        """
        return {int(k): v for k, v in self.decode_map.items()}
    
    def inspect(self) -> str:
        """
        Generate human-readable inspection output.
        
        Returns:
            Formatted string with key information
        """
        lines = [
            "=" * 50,
            "xEnco Key File Inspection",
            "=" * 50,
            f"Version:     {self.version}",
            f"Created:     {self.created}",
            f"Source:      {self.source}",
            f"ASCII Range: {self.ascii_from} - {self.ascii_to}",
            ""
        ]
        
        # Add checksum info
        if self._checksum:
            lines.append(f"Checksum:    {self._checksum[:20]}...")
        else:
            lines.append("Checksum:    (not calculated)")
        
        lines.extend([
            "",
            "-" * 50,
            "Character Mapping (first 10):",
            "-" * 50
        ])
        
        # Show first 10 mappings
        for i, (b64_char, key_char) in enumerate(self.encode_map.items()):
            if i >= 10:
                lines.append(f"... and {len(self.encode_map) - 10} more")
                break
            key_code = ord(key_char)
            lines.append(f"  {b64_char} -> '{key_char}' (code {key_code})")
        
        lines.extend([
            "",
            "-" * 50,
            "Key Statistics:",
            "-" * 50,
            f"Total mappings: {len(self.encode_map)}"
        ])
        
        # Check if source is accessible
        source_status = "unknown"
        if os.path.exists(self.source):
            source_status = "file (exists)"
        elif self.source.startswith(('http://', 'https://')):
            source_status = "URL"
        else:
            source_status = "raw text or unavailable"
        lines.append(f"Source type: {source_status}")
        
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def get_metadata(self) -> dict:
        """
        Get metadata dictionary.
        
        Returns:
            Dictionary with metadata (no key data)
        """
        return {
            "version": self.version,
            "created": self.created,
            "source": self.source,
            "ascii_from": self.ascii_from,
            "ascii_to": self.ascii_to,
            "checksum": self._checksum,
            "mapping_count": len(self.encode_map)
        }
    
    def mix(
        self,
        shift: Optional[int] = None,
        reverse: bool = False,
        seed: Optional[int] = None,
        permutation: Optional[List[int]] = None
    ) -> "KeyFile":
        """
        Create a new KeyFile by remixing the current key's source characters.

        The base64 key order stays the same, but the source characters that each
        base64 character maps to are reordered. This yields a different encoding
        while preserving the same source character set.

        Mixing methods (only one may be used at a time):
            shift: Rotate the source character list by N positions.
                   Example: shift=1 turns [a,b,c] into [c,a,b].
            reverse: Reverse the source character list.
            seed: Deterministically shuffle the source characters using
                  ``random.Random(seed)``.
            permutation: Explicitly reorder using a list of indices.
                          ``permutation=[2,0,1]`` means the new list is
                          ``[old[2], old[0], old[1]]``.

        Args:
            shift: Number of positions to rotate the character list.
            reverse: If True, reverse the character list.
            seed: Seed for deterministic random shuffle.
            permutation: Explicit permutation indices.

        Returns:
            A new KeyFile with remixed mappings.

        Raises:
            ValueError: If no mixing method is provided, multiple methods are
                        provided, or the permutation is invalid.

        Examples:
            >>> mixed = keyfile.mix(shift=5)
            >>> mixed = keyfile.mix(reverse=True)
            >>> mixed = keyfile.mix(seed=12345)
            >>> mixed = keyfile.mix(permutation=[2, 0, 1])
        """
        # Validate that exactly one mixing method is requested
        methods = [
            (shift is not None, "shift"),
            (reverse, "reverse"),
            (seed is not None, "seed"),
            (permutation is not None, "permutation"),
        ]
        selected = [name for active, name in methods if active]
        if len(selected) == 0:
            raise ValueError("No mixing method specified. Use one of: shift, reverse, seed, permutation")
        if len(selected) > 1:
            raise ValueError(f"Only one mixing method allowed, got: {', '.join(selected)}")

        # Extract source characters in base64 key order
        base64_chars = list(self.encode_map.keys())
        source_chars = [self.encode_map[b64] for b64 in base64_chars]
        count = len(source_chars)

        if count == 0:
            raise ValueError("Key has no character mappings to mix")

        # Apply the requested transformation
        if shift is not None:
            if not isinstance(shift, int):
                raise ValueError("shift must be an integer")
            new_source_chars = source_chars[-shift % count:] + source_chars[:-shift % count]
        elif reverse:
            new_source_chars = list(reversed(source_chars))
        elif seed is not None:
            rng = random.Random(seed)
            new_source_chars = source_chars[:]
            rng.shuffle(new_source_chars)
        else:  # permutation
            if len(permutation) != count:
                raise ValueError(
                    f"Permutation length ({len(permutation)}) must match "
                    f"number of mappings ({count})"
                )
            if sorted(permutation) != list(range(count)):
                raise ValueError(
                    "Permutation must contain each index exactly once, "
                    f"from 0 to {count - 1}"
                )
            new_source_chars = [source_chars[i] for i in permutation]

        # Build new encode/decode maps
        new_encode_map = {}
        new_decode_map = {}
        for b64_char, source_char in zip(base64_chars, new_source_chars):
            new_encode_map[b64_char] = source_char
            new_decode_map[ord(source_char)] = b64_char

        # Keep the same source/range; update creation time to now
        return KeyFile(
            encode_map=new_encode_map,
            decode_map=new_decode_map,
            source=self.source,
            ascii_from=self.ascii_from,
            ascii_to=self.ascii_to
        )

    @classmethod
    def from_keygenerator(cls, keygen, source: str) -> "KeyFile":
        """
        Create KeyFile from KeyGenerator and source.
        
        Args:
            keygen: KeyGenerator instance
            source: Source to generate key from
        
        Returns:
            KeyFile instance
        """
        encode_map, decode_map = keygen.generate(source)
        return cls(
            encode_map=encode_map,
            decode_map=decode_map,
            source=source,
            ascii_from=keygen.ascii_from,
            ascii_to=keygen.ascii_to
        )
