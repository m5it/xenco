#!/usr/bin/env python3
"""
Example: Simple Key Generation with generate_key()

This script demonstrates the convenient generate_key() function
for quick key generation without using the full KeyGenerator class.
"""

import tempfile
from pathlib import Path

# Import the convenient function
from xenco import generate_key
from xenco.keygen import InsufficientSourceError


def example_1_simple_url():
    """Example 1: Generate and save key from URL."""
    print("=" * 60)
    print("Example 1: Simple key generation from URL")
    print("=" * 60)
    
    # Note: Using a sample text instead of actual URL for demo
    # In real usage: generate_key("https://example.com", "mykey.xenco")
    source = "The quick brown fox jumps over the lazy dog. " * 10 + \
             "1234567890 !@#$%^&*() " * 5 + \
             "ABCDEFGHIJKLMNOPQRSTUVWXYZ " * 3
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "mykey.xenco"
        
        # Simple one-line key generation and save
        keyfile = generate_key(source, output_path=str(output_path))
        
        print(f"✓ Key generated and saved to: {output_path}")
        print(f"✓ Source: {keyfile.source}")
        print(f"✓ ASCII range: {keyfile.ascii_from}-{keyfile.ascii_to}")
        print(f"✓ Total mappings: {len(keyfile.encode_map)}")
        print()


def example_2_custom_ascii_range():
    """Example 2: Generate key with custom ASCII range."""
    print("=" * 60)
    print("Example 2: Custom ASCII range")
    print("=" * 60)
    
    # Source with characters in different ranges
    source = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" \
             "0123456789!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "custom_key.xenco"
        
        # Generate with custom ASCII range (40-120)
        keyfile = generate_key(
            source,
            output_path=str(output_path),
            ascii_from=40,  # Start at '(' character
            ascii_to=120,   # End at 'x' character
            pretty=True     # Pretty-print the JSON output
        )
        
        print(f"✓ Key generated with custom ASCII range")
        print(f"✓ Range: {keyfile.ascii_from}-{keyfile.ascii_to}")
        print(f"✓ Pretty-printed JSON: Yes")
        print(f"✓ File location: {output_path}")
        print()


def example_3_no_save():
    """Example 3: Generate key without saving (returns mappings)."""
    print("=" * 60)
    print("Example 3: Generate without saving")
    print("=" * 60)
    
    source = "The quick brown fox jumps over the lazy dog. " * 10 + \
             "1234567890 !@#$%^&*() " * 5 + \
             "ABCDEFGHIJKLMNOPQRSTUVWXYZ " * 3
    
    # Generate without output_path - returns tuple of mappings
    encode_map, decode_map = generate_key(source)
    
    print(f"✓ Key generated (not saved)")
    print(f"✓ Encode map type: {type(encode_map).__name__}")
    print(f"✓ Decode map type: {type(decode_map).__name__}")
    print(f"✓ Number of mappings: {len(encode_map)}")
    print(f"✓ Sample mapping: 'A' -> '{encode_map.get('A', 'N/A')}'")
    print()
    
    # You can now use these mappings directly with Encoder
    from xenco.encoder import Encoder
    
    encoder = Encoder(encode_map, decode_map)
    encoded = encoder.encode("Hello, World!")
    print(f"✓ Test encoding: 'Hello, World!' -> '{encoded}'")
    print()


def example_4_error_handling():
    """Example 4: Handle insufficient source error."""
    print("=" * 60)
    print("Example 4: Error handling")
    print("=" * 60)
    
    # This source doesn't have enough unique characters
    insufficient_source = "ABC"  # Only 3 unique chars, need 65
    
    try:
        generate_key(insufficient_source)
    except InsufficientSourceError as e:
        print(f"✓ Caught expected error:")
        print(f"  {e}")
        print()
        print("Tip: Use a larger source with more character diversity.")
        print("     Try a webpage URL, a large text file, or longer text.")
    print()


def main():
    """Run all examples."""
    print("\n")
    print("=" * 60)
    print("xEnco generate_key() Function Examples")
    print("=" * 60)
    print()
    
    example_1_simple_url()
    example_2_custom_ascii_range()
    example_3_no_save()
    example_4_error_handling()
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print()
    print("Summary:")
    print("  • generate_key(source, output_path) - Save to file")
    print("  • generate_key(source) - Return mappings only")
    print("  • Custom ASCII range with ascii_from/to parameters")
    print("  • Pretty-printed JSON with pretty=True")
    print()


if __name__ == "__main__":
    main()
