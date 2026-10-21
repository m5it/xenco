# xEnco 1.2.0

**Text Encoder/Decoder with Dynamic Key Generation**

xEnco is a Python package for encoding and decoding text using dynamically generated keys from any data source (URLs, files, or raw text). Each key creates a unique character mapping based on the source material, making encoded messages secure without traditional encryption algorithms.

## Features

- 🔑 **Dynamic Key Generation** - Create keys from URLs, files, or any text
- 🔄 **Bidirectional Encoding** - Encode/decode with the same key
- 💾 **Key Persistence** - Save and load keys in JSON format with checksums
- 📁 **File Support** - Process files of any size with streaming
- 🔧 **Configurable** - Custom ASCII ranges and HTTP settings
- 🧪 **Well Tested** - Comprehensive test suite with 80%+ coverage
- ✨ **Simple API** - One-line key generation with `generate_key()` (v1.1.0)
- 🚀 **Run Without Install** - `python main.py` launcher for direct usage
- 📦 **Batch Encoding** - Encode entire directories at once, as one file or separately (v1.2.0)
- 🎲 **Key Mixing** - Remix an existing key to produce different encodings (v1.2.0)
- 📂 **Directory Keys** - Generate keys from a directory of files (v1.2.0)

## Quick Start

### Installation
git clone https://github.com/m5it/xenco.git
```bash
# Clone the repository
git clone https://github.com/madk0s/xenco.git
cd xenco

# Install in development mode
pip install -e .

# Or install dependencies
pip install -r requirements.txt

# Or run directly without installing
python main.py --help
```

### Basic Usage

```bash
# Run without installing
python main.py --help

# Generate a key from a URL
python main.py keygen -s "https://www.example.com" -o mykey.xenco

# Or, after installation:
xenco keygen -s "https://www.example.com" -o mykey.xenco

# Encode a message
echo "Secret message" | xenco encode -k mykey.xenco -o encoded.txt

# Decode the message
xenco decode -i encoded.txt -k mykey.xenco -o -
```

## CLI Commands

### `keygen` - Generate a New Key

```bash
# From URL (default ASCII range 32-127)
xenco keygen -s "https://www.example.com" -o mykey.xenco

# From file
xenco keygen -s /path/to/source.txt -o mykey.xenco

# From raw text
xenco keygen -s "Your unique source text with many different characters..." -o mykey.xenco

# Custom ASCII range
xenco keygen -s "https://example.com" -o mykey.xenco -f 40 -t 127

# Pretty-printed JSON output
xenco keygen -s "https://example.com" -o mykey.xenco --pretty
```

### `mix` - Remix an Existing Key

```bash
# Rotate character positions
xenco mix -k mykey.xenco -o mixed.xenco --shift 5

# Reverse character order
xenco mix -k mykey.xenco -o mixed.xenco --reverse

# Deterministic shuffle by seed
xenco mix -k mykey.xenco -o mixed.xenco --seed 12345
```

### `batch` - Encode Multiple Files in a Directory

```bash
# Encode each file separately (creates file.txt.xenco next to every file)
xenco batch -d /path/to/dir -k mykey.xenco -m separate

# Encode everything into a single combined file
xenco batch -d /path/to/dir -k mykey.xenco -o combined.xenco -m one

# Write separated outputs to another directory, preserving structure
xenco batch -d /path/to/dir -k mykey.xenco -o /path/to/out -m separate

# Only process top-level files, ignore subdirectories
xenco batch -d /path/to/dir -k mykey.xenco --no-recursive
```

### `encode` - Encode Text

```bash
# Encode from stdin
echo "Hello, World!" | xenco encode -k mykey.xenco

# Encode from file
xenco encode -i message.txt -k mykey.xenco -o encoded.txt

# Encode with verbose output
xenco encode -i message.txt -k mykey.xenco -o encoded.txt -v
```

### `decode` - Decode Text

```bash
# Decode to stdout
xenco decode -i encoded.txt -k mykey.xenco -o -

# Decode from stdin
cat encoded.txt | xenco decode -k mykey.xenco

# Decode quietly
xenco decode -i encoded.txt -k mykey.xenco -o decoded.txt -q
```

### `inspect` - View Key Information

```bash
# Full inspection
xenco inspect -k mykey.xenco

# Metadata only
xenco inspect -k mykey.xenco --metadata
```

## Python API

### Quick Key Generation (New in 1.1.0)

```python
from xenco import generate_key

# Generate from text and save to file (NO INTERNET REQUIRED)
keyfile = generate_key("Your source text with many unique characters...", "mykey.xenco")

# Generate from a local file
keyfile = generate_key("/path/to/source.txt", "mykey.xenco")

# Generate with custom options
keyfile = generate_key(
    "source text here...",
    output_path="key.xenco",
    ascii_from=40,
    ascii_to=120,
    pretty=True
)

# Generate without saving - returns mappings tuple
encode_map, decode_map = generate_key("my source text...")
```

**Note:** `generate_key()` works with any source - text strings, local files, directories, or URLs. No internet required for text, file, or directory sources!

### Batch Encoding API

```python
from xenco.batch import encode_batch, decode_combined

# Encode all files in a directory separately
result = encode_batch("/path/to/dir", "mykey.xenco", mode="separate")

# Encode everything into one combined file
encode_batch("/path/to/dir", "mykey.xenco", output="combined.xenco", mode="one")

# Decode a combined batch file back into (path, content) tuples
files = decode_combined(open("combined.xenco").read(), "mykey.xenco")
for relative_path, content in files:
    print(relative_path, content)
```

### Remixing a Key

```python
from xenco.keyfile import KeyFile

keyfile = KeyFile.load("mykey.xenco")

# Shift character positions
mixed = keyfile.mix(shift=5)

# Reverse the character order
mixed = keyfile.mix(reverse=True)

# Deterministic shuffle by seed
mixed = keyfile.mix(seed=12345)

# Save the mixed key
mixed.save("mixed.xenco")
```

# Generate a key
keygen = KeyGenerator(ascii_from=32, ascii_to=127)
encode_map, decode_map = keygen.generate("https://www.example.com")

# Create encoder
encoder = Encoder(encode_map, decode_map)

# Encode
encoded = encoder.encode("Hello, World!")

# Decode
decoded = encoder.decode(encoded)
print(decoded)  # Hello, World!
```

### Working with Key Files

```python
from xenco.keyfile import KeyFile
from xenco.keygen import KeyGenerator

# Generate and save key
keygen = KeyGenerator(32, 127)
keyfile = KeyFile.from_keygenerator(keygen, "https://example.com")
keyfile.save("mykey.xenco")

# Load key
loaded = KeyFile.load("mykey.xenco")
encoder = Encoder(loaded.encode_map, loaded.get_decode_map_int())
```

### Configuration

```python
from xenco.config import Config

# Load/create config
config = Config()

# Access settings
print(config.ascii_from)  # 32
print(config.ascii_to)    # 127

# Modify settings
config.ascii_from = 40
config.http_timeout = 60
config.save()
```

## Key File Format

xEnco keys are stored in JSON format with metadata:

```json
{
  "version": "1.2.0",
  "created": "2024-01-15T10:30:00",
  "source": "https://www.example.com",
  "ascii_range": {
    "from": 32,
    "to": 127
  },
  "checksum": "sha256:abc123...",
  "encode_map": {
    "A": "!",
    "B": "@",
    "C": "#",
    "...": "..."
  },
  "decode_map": {
    "33": "A",
    "64": "B",
    "35": "C",
    "...": "..."
  }
}
```

## How It Works

1. **Key Generation**: Extracts unique characters from the source within the specified ASCII range
2. **Mapping Creation**: Maps base64 characters (A-Z, a-z, 0-9, +/=) to the source characters (65 total)
3. **Encoding**: Converts text to base64, then maps each character using the key
4. **Decoding**: Reverse mapping from encoded characters back to base64, then decodes

## Troubleshooting

### "Source contains only X unique characters"

Your source doesn't have enough unique characters in the ASCII range. Try:
- Using a different source (larger webpage, bigger file)
- Expanding the ASCII range: `-f 32 -t 127`

### "Key file checksum mismatch"

The key file may be corrupted. Regenerate the key from the original source.

### "Text contains characters not in key"

You're using the wrong key file for this encoded text. Use the key that was used for encoding.

## Requirements

- Python 3.7+
- requests >= 2.25.0

## License

MIT License - See LICENSE file for details

## Author

madK0s

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
