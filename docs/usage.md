# xEnco Usage Guide

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [CLI Reference](#cli-reference)
4. [Python API](#python-api)
5. [Examples](#examples)

## Installation

### From Source
git clone https://github.com/m5it/xenco.git
```bash
git clone https://github.com/madk0s/xenco.git
cd xenco
pip install -e .
```

### Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### Generate Your First Key

```bash
# Using a website as source
xenco keygen -s "https://en.wikipedia.org/wiki/Main_Page" -o wiki_key.xenco

# Using a text file
xenco keygen -s /usr/share/dict/words -o dict_key.xenco
```

### Encode a Secret Message

```bash
echo "Meet at the old oak tree at midnight" | xenco encode -k wiki_key.xenco > secret.txt
```

### Decode the Message

```bash
xenco decode -i secret.txt -k wiki_key.xenco
```

## CLI Reference

### Global Options

| Option | Description |
|--------|-------------|
| `-V, --version` | Show version and exit |
| `-v, --verbose` | Enable verbose output |
| `-q, --quiet` | Suppress non-error output |

### Commands

#### `keygen` - Generate a Key

**Usage:** `xenco keygen -s SOURCE -o OUTPUT [options]`

**Required Arguments:**
- `-s, --source` - Source data (URL, file path, or text)
- `-o, --output` - Output key file path

**Optional Arguments:**
- `-f, --from` - ASCII range start (default: 32)
- `-t, --to` - ASCII range end (default: 128)
- `--pretty` - Pretty-print JSON output

**Examples:**

```bash
# Basic usage
xenco keygen -s "https://example.com" -o key.xenco

# Custom ASCII range
xenco keygen -s "source.txt" -o key.xenco -f 40 -t 120

# Pretty output
xenco keygen -s "https://example.com" -o key.xenco --pretty
```

#### `encode` - Encode Text

**Usage:** `xenco encode -k KEY [-i INPUT] [-o OUTPUT]`

**Required Arguments:**
- `-k, --key` - Key file to use

**Optional Arguments:**
- `-i, --input` - Input file (default: stdin)
- `-o, --output` - Output file (default: stdout)

**Examples:**

```bash
# From stdin to stdout
echo "message" | xenco encode -k key.xenco

# From file to file
xenco encode -i plain.txt -k key.xenco -o encoded.txt

# From stdin to file
cat message.txt | xenco encode -k key.xenco -o encoded.txt
```

#### `decode` - Decode Text

**Usage:** `xenco decode -k KEY [-i INPUT] [-o OUTPUT]`

**Required Arguments:**
- `-k, --key` - Key file to use

**Optional Arguments:**
- `-i, --input` - Input file (default: stdin)
- `-o, --output` - Output file (default: stdout)

**Examples:**

```bash
# Decode to stdout
xenco decode -i encoded.txt -k key.xenco

# Decode to file
xenco decode -i encoded.txt -k key.xenco -o decoded.txt

# From stdin
cat encoded.txt | xenco decode -k key.xenco
```

#### `inspect` - Inspect Key File

**Usage:** `xenco inspect -k KEY [--metadata]`

**Required Arguments:**
- `-k, --key` - Key file to inspect

**Optional Arguments:**
- `--metadata` - Show only metadata

**Examples:**

```bash
# Full inspection
xenco inspect -k key.xenco

# Metadata only
xenco inspect -k key.xenco --metadata
```

## Python API

### Basic Usage

```python
from xenco.keygen import KeyGenerator
from xenco.encoder import Encoder
from xenco.keyfile import KeyFile

# Generate key
keygen = KeyGenerator(ascii_from=32, ascii_to=128)
encode_map, decode_map = keygen.generate("https://example.com")

# Create encoder
encoder = Encoder(encode_map, decode_map)

# Encode/decode
encoded = encoder.encode("Secret message")
decoded = encoder.decode(encoded)
```

### Working with Files

```python
from xenco.utils import read_text_file, write_text_file

# Read file
content = read_text_file("message.txt")

# Write file
write_text_file("output.txt", encoded_content)
```

### Streaming Large Files

```python
# Encode large file
with open("large_input.txt", "rb") as infile:
    with open("encoded.txt", "w") as outfile:
        encoder.encode_stream(infile, outfile)

# Decode large file
with open("encoded.txt", "r") as infile:
    with open("decoded.txt", "wb") as outfile:
        encoder.decode_stream(infile, outfile)
```

## Examples

### Example 1: Secure Message Exchange

```bash
# Alice generates a key from a shared source
xenco keygen -s "https://news.ycombinator.com" -o shared_key.xenco

# Alice encodes a message
echo "The package is ready" | xenco encode -k shared_key.xenco > message.txt

# Alice sends message.txt to Bob
# Bob decodes using the same key
xenco decode -i message.txt -k shared_key.xenco
```

### Example 2: File Encryption Script

```bash
#!/bin/bash
# encrypt.sh - Encrypt files using xenco

KEY_FILE="mykey.xenco"
INPUT_FILE="$1"

if [ -z "$INPUT_FILE" ]; then
    echo "Usage: $0 <file>"
    exit 1
fi

OUTPUT_FILE="${INPUT_FILE}.enc"

xenco encode -i "$INPUT_FILE" -k "$KEY_FILE" -o "$OUTPUT_FILE"
echo "Encrypted to: $OUTPUT_FILE"
```

### Example 3: Batch Processing

```bash
# Encode all .txt files in a directory
for file in *.txt; do
    xenco encode -i "$file" -k master_key.xenco -o "${file}.enc"
done

# Decode all .enc files
for file in *.enc; do
    xenco decode -i "$file" -k master_key.xenco -o "${file%.enc}.dec"
done
```
