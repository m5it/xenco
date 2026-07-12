# xEnco Examples

This directory contains example scripts and data files demonstrating xEnco usage.

## Example Scripts

### `generate_key.py`

Demonstrates key generation from different sources.

```bash
python examples/generate_key.py
```

**Features:**
- Generate key from URL
- Generate key from file
- Generate key from raw text
- Error handling for insufficient sources

### `encode_decode.py`

Complete workflow example showing encoding and decoding.

```bash
python examples/encode_decode.py
```

**Features:**
- Generate key from source text
- Encode multiple messages
- Decode messages back
- Verify round-trip integrity
- Demonstrate wrong key detection

## Sample Data

### `sample_source.txt`

A text file with sufficient unique characters for key generation.

```bash
# Generate key from sample
xenco keygen -s examples/sample_source.txt -o sample_key.xenco

# Use for encoding
echo "Secret message" | xenco encode -k sample_key.xenco
```

## Use Cases

### Secure Communication

Alice and Bob share a key generated from a public webpage:

```bash
# Both generate the same key
xenco keygen -s "https://news.ycombinator.com" -o shared_key.xenco

# Alice encodes
echo "Meet at 3pm" | xenco encode -k shared_key.xenco > message.txt

# Bob decodes
xenco decode -i message.txt -k shared_key.xenco
```

### File Protection

Protect sensitive files with encoding:

```bash
# Create key
xenco keygen -s "https://example.com/special-page" -o secret_key.xenco

# Encode file
xenco encode -i secrets.txt -k secret_key.xenco -o secrets.txt.enc

# Later, decode
xenco decode -i secrets.txt.enc -k secret_key.xenco -o secrets.txt
```

### Batch Processing

Process multiple files:

```bash
#!/bin/bash
KEY="mykey.xenco"

for file in *.txt; do
    xenco encode -i "$file" -k "$KEY" -o "${file}.enc"
    echo "Encoded: $file -> ${file}.enc"
done
```

### Python Integration

Use xEnco in your Python scripts:

```python
from xenco.keygen import KeyGenerator
from xenco.encoder import Encoder

# Generate key
keygen = KeyGenerator(32, 128)
encode_map, decode_map = keygen.generate("source")

# Create encoder
encoder = Encoder(encode_map, decode_map)

# Process data
encoded = encoder.encode("Sensitive data")
# Store or transmit encoded
decoded = encoder.decode(encoded)
```
