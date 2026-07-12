#!/usr/bin/env python3
"""
Example: Generate a key from various sources.

This script demonstrates how to generate keys from URLs, files, and text.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from xenco.keygen import KeyGenerator, InsufficientSourceError
from xenco.keyfile import KeyFile


def generate_from_url(url, output_file):
    """Generate key from a URL."""
    print(f"Generating key from URL: {url}")
    
    keygen = KeyGenerator(ascii_from=32, ascii_to=128)
    
    try:
        keyfile = KeyFile.from_keygenerator(keygen, url)
        keyfile.save(output_file, pretty=True)
        print(f"Key saved to: {output_file}")
        
        # Show info
        info = keyfile.get_metadata()
        print(f"Unique characters: {info['mapping_count']}")
        print(f"ASCII range: {info['ascii_from']}-{info['ascii_to']}")
        
    except InsufficientSourceError as e:
        print(f"Error: {e}")
        print("Try using a different URL or expanding the ASCII range.")


def generate_from_file(filepath, output_file):
    """Generate key from a file."""
    print(f"Generating key from file: {filepath}")
    
    keygen = KeyGenerator(ascii_from=32, ascii_to=128)
    
    try:
        keyfile = KeyFile.from_keygenerator(keygen, filepath)
        keyfile.save(output_file, pretty=True)
        print(f"Key saved to: {output_file}")
        
    except InsufficientSourceError as e:
        print(f"Error: {e}")
        print("Try using a larger file or expanding the ASCII range.")


def generate_from_text(text, output_file):
    """Generate key from raw text."""
    print(f"Generating key from text ({len(text)} chars)")
    
    keygen = KeyGenerator(ascii_from=32, ascii_to=128)
    
    try:
        keyfile = KeyFile.from_keygenerator(keygen, text)
        keyfile.save(output_file, pretty=True)
        print(f"Key saved to: {output_file}")
        
    except InsufficientSourceError as e:
        print(f"Error: {e}")
        print("The text doesn't have enough unique characters.")


if __name__ == "__main__":
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Example 1: Generate from URL
        print("=" * 50)
        print("Example 1: Generate from URL")
        print("=" * 50)
        generate_from_url(
            "https://en.wikipedia.org/wiki/Main_Page",
            f"{tmpdir}/wiki_key.xenco"
        )
        
        # Example 2: Generate from file
        print("\n" + "=" * 50)
        print("Example 2: Generate from file")
        print("=" * 50)
        
        # Create a sample file
        sample_file = Path(tmpdir) / "sample.txt"
        sample_file.write_text(
            "The quick brown fox jumps over the lazy dog. " * 100 +
            "1234567890 !@#$%^&*() " * 50 +
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ " * 20
        )
        
        generate_from_file(str(sample_file), f"{tmpdir}/file_key.xenco")
        
        # Example 3: Generate from text
        print("\n" + "=" * 50)
        print("Example 3: Generate from text")
        print("=" * 50)
        
        sample_text = (
            "The quick brown fox jumps over the lazy dog. " * 100 +
            "1234567890 !@#$%^&*() " * 50 +
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ " * 20
        )
        
        generate_from_text(sample_text, f"{tmpdir}/text_key.xenco")
        
        print("\nAll examples completed successfully!")
