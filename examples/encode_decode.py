#!/usr/bin/env python3
"""
Example: Encode and decode messages.

This script demonstrates the full workflow of encoding and decoding text.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from xenco.keygen import KeyGenerator
from xenco.encoder import Encoder
from xenco.keyfile import KeyFile


def main():
    # Sample source with many unique characters
    source_text = """
    The quick brown fox jumps over the lazy dog.
    THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG.
    1234567890 !@#$%^&*()_+-=[]{}|;':\",./<>?
    abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ
    0123456789 `~!@#$%^&*()_+-=[]{}|\\;':\",./<>?
    """
    
    print("=" * 60)
    print("xEnco Encode/Decode Example")
    print("=" * 60)
    
    # Step 1: Generate a key
    print("\n1. Generating key from source text...")
    keygen = KeyGenerator(ascii_from=32, ascii_to=128)
    keyfile = KeyFile.from_keygenerator(keygen, source_text)
    
    # Save key for later use
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        key_path = Path(tmpdir) / "example_key.xenco"
        keyfile.save(str(key_path))
        print(f"   Key saved to: {key_path}")
        
        # Step 2: Create encoder
        print("\n2. Creating encoder...")
        encoder = Encoder(keyfile.encode_map, keyfile.get_decode_map_int())
        print("   Encoder ready")
        
        # Step 3: Encode messages
        messages = [
            "Hello, World!",
            "The password is swordfish123",
            "Meet me at the usual place",
            "Top secret: the cake is a lie"
        ]
        
        print("\n3. Encoding messages:")
        encoded_messages = []
        
        for msg in messages:
            encoded = encoder.encode(msg)
            encoded_messages.append(encoded)
            print(f"   Original: {msg}")
            print(f"   Encoded:  {encoded}")
            print()
        
        # Step 4: Decode messages
        print("4. Decoding messages:")
        
        for original, encoded in zip(messages, encoded_messages):
            decoded = encoder.decode(encoded)
            print(f"   Encoded:  {encoded}")
            print(f"   Decoded:  {decoded}")
            print(f"   Match:    {original == decoded}")
            print()
        
        # Step 5: Demonstrate wrong key failure
        print("5. Demonstrating wrong key detection:")
        
        # Generate a different key
        different_source = "Completely different source material " * 50
        different_keygen = KeyGenerator(32, 128)
        different_keyfile = KeyFile.from_keygenerator(different_keygen, different_source)
        different_encoder = Encoder(
            different_keyfile.encode_map,
            different_keyfile.get_decode_map_int()
        )
        
        # Try to decode with wrong key
        try:
            wrong_decode = different_encoder.decode(encoded_messages[0])
            print(f"   Wrong decode result: {wrong_decode}")
        except Exception as e:
            print(f"   Correctly failed with wrong key: {type(e).__name__}")
        
        print("\n" + "=" * 60)
        print("Example completed!")
        print("=" * 60)


if __name__ == "__main__":
    main()
