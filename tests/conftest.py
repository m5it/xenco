"""
pytest configuration and fixtures for xenco tests.
"""

import pytest
import tempfile
import os
from pathlib import Path


# Sample source with sufficient unique characters (ASCII 32-128)
SAMPLE_SOURCE = """
The quick brown fox jumps over the lazy dog.
1234567890 !@#$%^&*()_+-=[]{}|;':\",./<>?
ABCDEFGHIJKLMNOPQRSTUVWXYZ
abcdefghijklmnopqrstuvwxyz
More characters: ~`¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿
ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ
"""


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_source_file(temp_dir):
    """Create a sample source file with sufficient unique characters."""
    source_path = temp_dir / "sample_source.txt"
    source_path.write_text(SAMPLE_SOURCE)
    return str(source_path)


@pytest.fixture
def sample_source_text():
    """Return sample source text."""
    return SAMPLE_SOURCE


@pytest.fixture
def mock_key_mappings():
    """Return mock key mappings for testing."""
    # Simple mapping: A->!, B->@, C->#, etc.
    encode_map = {
        'A': '!', 'B': '@', 'C': '#', 'D': '$', 'E': '%', 'F': '^',
        'G': '&', 'H': '*', 'I': '(', 'J': ')', 'K': '-', 'L': '=',
        'M': '+', 'N': '[', 'O': ']', 'P': '{', 'Q': '}', 'R': '|',
        'S': ';', 'T': ':', 'U': "'", 'V': '"', 'W': ',', 'X': '.',
        'Y': '<', 'Z': '>',
        'a': '1', 'b': '2', 'c': '3', 'd': '4', 'e': '5', 'f': '6',
        'g': '7', 'h': '8', 'i': '9', 'j': '0', 'k': 'a', 'l': 'b',
        'm': 'c', 'n': 'd', 'o': 'e', 'p': 'f', 'q': 'g', 'r': 'h',
        's': 'i', 't': 'j', 'u': 'k', 'v': 'l', 'w': 'm', 'x': 'n',
        'y': 'o', 'z': 'p',
        '0': 'q', '1': 'r', '2': 's', '3': 't', '4': 'u', '5': 'v',
        '6': 'w', '7': 'x', '8': 'y', '9': 'z',
        '+': 'Q', '/': 'W'
    }
    
    # Create decode_map from encode_map
    decode_map = {ord(v): k for k, v in encode_map.items()}
    
    return encode_map, decode_map


@pytest.fixture
def sample_key_file(temp_dir, mock_key_mappings):
    """Create a sample key file for testing."""
    from xenco.keyfile import KeyFile
    
    encode_map, decode_map = mock_key_mappings
    keyfile = KeyFile(
        encode_map=encode_map,
        decode_map=decode_map,
        source="test_source",
        ascii_from=32,
        ascii_to=128
    )
    
    key_path = temp_dir / "test_key.xenco"
    keyfile.save(str(key_path))
    return str(key_path)
