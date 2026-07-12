"""
xEnco Validation

Comprehensive validation for keys, sources, and encoded data.
"""

import os
import re
from typing import Dict, Optional, Set, Union
from pathlib import Path


# Base64 character set for validation (64 + padding)
BASE64_CHARS = set(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    "+/="
)


class XencoError(Exception):
    """
    Base exception for all xenco errors.
    
    All other exceptions in this module inherit from this.
    """
    pass


class ValidationError(XencoError):
    """
    Exception raised for validation failures.
    
    Attributes:
        message (str): Error message
        field (str): Field that failed validation
    """
    
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        if self.field:
            return f"Validation error in '{self.field}': {self.message}"
        return f"Validation error: {self.message}"


class SourceError(ValidationError):
    """
    Exception raised for source data errors.
    
    This includes invalid URLs, unreadable files, or insufficient
    character diversity in source material.
    """
    pass


class KeyError(ValidationError):
    """
    Exception raised for key-related errors.
    
    This includes incomplete mappings, checksum failures, or
    incompatible key versions.
    """
    pass


class InputError(ValidationError):
    """
    Exception raised for input data errors.
    
    This includes text that cannot be encoded with the given key.
    """
    pass


class Validator:
    """
    Comprehensive validation for xenco operations.
    
    Provides static methods for validating all aspects of the
    encoding/decoding pipeline.
    """
    
    # Minimum unique characters required for base64 encoding (65 = 64 + padding)
    MIN_UNIQUE_CHARS = 65
    # Maximum valid ASCII code
    MAX_ASCII = 127
    
    @staticmethod
    def validate_ascii_range(ascii_from: int, ascii_to: int) -> None:
        """
        Validate ASCII range parameters.
        
        Args:
            ascii_from: Starting ASCII code (inclusive)
            ascii_to: Ending ASCII code (inclusive)
        
        Raises:
            ValidationError: If range is invalid
        """
        # Check types
        if not isinstance(ascii_from, int) or not isinstance(ascii_to, int):
            raise ValidationError(
                "ASCII range values must be integers",
                field="ascii_range"
            )
        
        # Check bounds
        if ascii_from < 0:
            raise ValidationError(
                f"ASCII 'from' value ({ascii_from}) must be >= 0",
                field="ascii_from"
            )
        
        if ascii_to > Validator.MAX_ASCII:
            raise ValidationError(
                f"ASCII 'to' value ({ascii_to}) must be <= {Validator.MAX_ASCII}",
                field="ascii_to"
            )
        
        # Check relationship
        if ascii_from >= ascii_to:
            raise ValidationError(
                f"ASCII 'from' ({ascii_from}) must be less than 'to' ({ascii_to})",
                field="ascii_range"
            )
        
        # Check range size (need at least 65 characters)
        range_size = ascii_to - ascii_from + 1
        if range_size < Validator.MIN_UNIQUE_CHARS:
            raise ValidationError(
                f"ASCII range size ({range_size}) is too small. "
                f"Need at least {Validator.MIN_UNIQUE_CHARS} characters.",
                field="ascii_range"
            )
    
    @staticmethod
    def validate_source_content(
        content: str,
        ascii_from: int,
        ascii_to: int
    ) -> Set[str]:
        """
        Validate source content has sufficient unique characters.
        
        Args:
            content: Source content to validate
            ascii_from: ASCII range start
            ascii_to: ASCII range end
        
        Returns:
            Set of unique characters found in range
        
        Raises:
            SourceError: If content is insufficient
        """
        if not content:
            raise SourceError(
                "Source content is empty",
                field="source"
            )
        
        # Extract unique characters in range
        unique_chars = set()
        for char in content:
            code = ord(char)
            if ascii_from <= code <= ascii_to:
                unique_chars.add(char)
        
        # Check count
        count = len(unique_chars)
        if count < Validator.MIN_UNIQUE_CHARS:
            raise SourceError(
                f"Source contains only {count} unique characters in range "
                f"[{ascii_from}-{ascii_to}], but {Validator.MIN_UNIQUE_CHARS} are required. "
                f"Need {Validator.MIN_UNIQUE_CHARS - count} more unique characters. "
                f"Consider using a different source or expanding the ASCII range.",
                field="source"
            )
        
        return unique_chars
    
    @staticmethod
    def validate_source_type(source: str) -> str:
        """
        Validate and classify source type.
        
        Args:
            source: Source string (URL, path, or text)
        
        Returns:
            Source type: 'url', 'file', or 'text'
        
        Raises:
            SourceError: If source is invalid
        """
        if not source:
            raise SourceError(
                "Source cannot be empty",
                field="source"
            )
        
        # Check if URL
        if re.match(r'^https?://', source, re.IGNORECASE):
            return 'url'
        
        # Check if file exists
        if os.path.exists(source):
            if os.path.isfile(source):
                return 'file'
            else:
                raise SourceError(
                    f"Source path exists but is not a file: {source}",
                    field="source"
                )
        
        # Treat as raw text
        return 'text'
    
    @staticmethod
    def validate_key_mappings(
        encode_map: Dict[str, str],
        decode_map: Dict[int, str]
    ) -> None:
        """
        Validate key mappings are complete and consistent.
        
        Args:
            encode_map: Maps base64 chars to key chars
            decode_map: Maps key char codes to base64 chars
        
        Raises:
            KeyError: If mappings are invalid
        """
        # Check encode_map has all base64 characters
        missing = BASE64_CHARS - set(encode_map.keys())
        if missing:
            raise KeyError(
                f"Key mapping incomplete. Missing base64 characters: {sorted(missing)}",
                field="encode_map"
            )
        
        # Check for extra characters in encode_map
        extra = set(encode_map.keys()) - BASE64_CHARS
        if extra:
            raise KeyError(
                f"Key mapping contains invalid base64 characters: {sorted(extra)}",
                field="encode_map"
            )
        
        # Check decode_map has all required entries
        for b64_char, key_char in encode_map.items():
            key_code = ord(key_char)
            
            if key_code not in decode_map:
                raise KeyError(
                    f"Decode map missing entry for key character '{key_char}' "
                    f"(code {key_code}) which maps to base64 '{b64_char}'",
                    field="decode_map"
                )
            
            if decode_map[key_code] != b64_char:
                raise KeyError(
                    f"Decode map inconsistent: code {key_code} maps to "
                    f"'{decode_map[key_code]}' but encode map expects '{b64_char}'",
                    field="decode_map"
                )
        
        # Check decode_map has no extra entries
        expected_codes = {ord(encode_map[b64]) for b64 in BASE64_CHARS}
        extra_codes = set(decode_map.keys()) - expected_codes
        if extra_codes:
            raise KeyError(
                f"Decode map contains unexpected codes: {sorted(extra_codes)}",
                field="decode_map"
            )
    
    @staticmethod
    def validate_key_file_data(data: dict) -> None:
        """
        Validate key file data structure.
        
        Args:
            data: Parsed key file dictionary
        
        Raises:
            KeyError: If key file data is invalid
        """
        required_fields = ['version', 'encode_map', 'decode_map', 'source']
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                raise KeyError(
                    f"Key file missing required field: {field}",
                    field=field
                )
        
        # Validate version
        version = data.get('version')
        if not isinstance(version, str):
            raise KeyError(
                f"Key file version must be a string, got {type(version).__name__}",
                field='version'
            )
        
        # Validate ASCII range if present
        ascii_range = data.get('ascii_range', {})
        if 'from' in ascii_range and 'to' in ascii_range:
            try:
                Validator.validate_ascii_range(
                    ascii_range['from'],
                    ascii_range['to']
                )
            except ValidationError as e:
                raise KeyError(str(e), field='ascii_range')
        
        # Validate mappings
        encode_map = data.get('encode_map', {})
        decode_map_raw = data.get('decode_map', {})
        
        # Convert decode_map keys to integers if they're strings
        decode_map = {}
        for k, v in decode_map_raw.items():
            try:
                decode_map[int(k)] = v
            except (ValueError, TypeError):
                raise KeyError(
                    f"Decode map has non-integer key: {k!r}",
                    field='decode_map'
                )
        
        Validator.validate_key_mappings(encode_map, decode_map)
    
    @staticmethod
    def validate_encodable_text(text: str, encode_map: Dict[str, str]) -> None:
        """
        Validate text can be encoded with given key.
        
        Note: Since encoding uses base64 first, any text is technically
        encodable. This validates the key itself can handle base64 output.
        
        Args:
            text: Text to validate
            encode_map: Key encode mapping
        
        Raises:
            InputError: If text cannot be encoded
        """
        if text is None:
            raise InputError(
                "Input text cannot be None",
                field="input"
            )
        
        # All text is encodable (goes through base64 first)
        # But we should validate the key can handle it
        if not encode_map:
            raise KeyError(
                "Encode map is empty",
                field="encode_map"
            )
    
    @staticmethod
    def validate_decodable_text(text: str, decode_map: Dict[int, str]) -> None:
        """
        Validate encoded text can be decoded with given key.
        
        Args:
            text: Encoded text to validate
            decode_map: Key decode mapping (code -> base64 char)
        
        Raises:
            InputError: If text cannot be decoded
        """
        if text is None:
            raise InputError(
                "Input text cannot be None",
                field="input"
            )
        
        if not text:
            # Empty text is valid (decodes to empty)
            return
        
        # Check all characters are in decode_map
        invalid_chars = []
        for i, char in enumerate(text):
            code = ord(char)
            if code not in decode_map:
                invalid_chars.append((i, char, code))
        
        if invalid_chars:
            # Show first few invalid characters
            samples = invalid_chars[:3]
            sample_str = ", ".join(
                f"'{c}' (code {code}) at position {pos}"
                for pos, c, code in samples
            )
            if len(invalid_chars) > 3:
                sample_str += f", and {len(invalid_chars) - 3} more"
            
            raise InputError(
                f"Text contains characters not in key: {sample_str}. "
                f"Make sure you're using the correct key file for this encoded text.",
                field="input"
            )
    
    @staticmethod
    def validate_file_path(
        path: Union[str, Path],
        must_exist: bool = False,
        must_not_exist: bool = False,
        must_be_file: bool = False,
        must_be_dir: bool = False,
        readable: bool = False,
        writable: bool = False
    ) -> Path:
        """
        Validate file path meets requirements.
        
        Args:
            path: Path to validate
            must_exist: Path must exist
            must_not_exist: Path must not exist
            must_be_file: Path must be a file
            must_be_dir: Path must be a directory
            readable: Path must be readable
            writable: Path must be writable (parent dir for new files)
        
        Returns:
            Validated Path object
        
        Raises:
            ValidationError: If path doesn't meet requirements
        """
        path = Path(path)
        
        # Check existence requirements
        if must_exist and not path.exists():
            raise ValidationError(
                f"Path does not exist: {path}",
                field="path"
            )
        
        if must_not_exist and path.exists():
            raise ValidationError(
                f"Path already exists: {path}",
                field="path"
            )
        
        # Check type requirements
        if must_be_file and path.exists() and not path.is_file():
            raise ValidationError(
                f"Path is not a file: {path}",
                field="path"
            )
        
        if must_be_dir and path.exists() and not path.is_dir():
            raise ValidationError(
                f"Path is not a directory: {path}",
                field="path"
            )
        
        # Check readability
        if readable and path.exists():
            if not os.access(path, os.R_OK):
                raise ValidationError(
                    f"Path is not readable: {path}",
                    field="path"
                )
        
        # Check writability
        if writable:
            if path.exists():
                if not os.access(path, os.W_OK):
                    raise ValidationError(
                        f"Path is not writable: {path}",
                        field="path"
                    )
            else:
                # Check parent directory
                parent = path.parent
                if not parent.exists():
                    raise ValidationError(
                        f"Parent directory does not exist: {parent}",
                        field="path"
                    )
                if not os.access(parent, os.W_OK):
                    raise ValidationError(
                        f"Parent directory is not writable: {parent}",
                        field="path"
                    )
        
        return path


# Convenience function for quick validation
def validate_all(
    ascii_from: Optional[int] = None,
    ascii_to: Optional[int] = None,
    source: Optional[str] = None,
    key_file: Optional[dict] = None,
    input_text: Optional[str] = None,
    encode_map: Optional[Dict[str, str]] = None,
    decode_map: Optional[Dict[int, str]] = None
) -> dict:
    """
    Run all applicable validations and return results.
    
    Returns a dictionary with validation results.
    """
    results = {
        'valid': True,
        'errors': []
    }
    
    try:
        if ascii_from is not None and ascii_to is not None:
            Validator.validate_ascii_range(ascii_from, ascii_to)
    except ValidationError as e:
        results['valid'] = False
        results['errors'].append(str(e))
    
    try:
        if source is not None:
            Validator.validate_source_type(source)
    except ValidationError as e:
        results['valid'] = False
        results['errors'].append(str(e))
    
    try:
        if key_file is not None:
            Validator.validate_key_file_data(key_file)
    except ValidationError as e:
        results['valid'] = False
        results['errors'].append(str(e))
    
    try:
        if encode_map is not None and decode_map is not None:
            Validator.validate_key_mappings(encode_map, decode_map)
    except ValidationError as e:
        results['valid'] = False
        results['errors'].append(str(e))
    
    return results
