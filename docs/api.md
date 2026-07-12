# xEnco Python API Documentation

## Core Modules

### `xenco.keygen`

Key generation from data sources.

#### `KeyGenerator`

```python
from xenco.keygen import KeyGenerator, InsufficientSourceError

# Initialize with ASCII range
keygen = KeyGenerator(ascii_from=32, ascii_to=128)

# Generate key from source
encode_map, decode_map = keygen.generate("https://example.com")

# Get info about source without generating
info = keygen.get_key_info("source.txt")
print(f"Unique chars: {info['unique_chars']}")
```

**Constructor:**
- `ascii_from` (int): Starting ASCII code (default: 32)
- `ascii_to` (int): Ending ASCII code (default: 128)

**Methods:**
- `generate(source: str) -> Tuple[Dict[str, str], Dict[int, str]]` - Generate key mappings
- `get_key_info(source: str) -> dict` - Get source information
- `clear_cache()` - Clear content cache

**Exceptions:**
- `InsufficientSourceError` - Source has < 64 unique characters
- `KeyGenerationError` - General key generation failure

---

### `xenco.encoder`

Encoding and decoding operations.

#### `Encoder`

```python
from xenco.encoder import Encoder, EncodingError

# Create with mappings from KeyGenerator
encoder = Encoder(encode_map, decode_map)

# Encode
encoded = encoder.encode("Hello, World!")

# Decode
decoded = encoder.decode(encoded)
```

**Constructor:**
- `encode_map` (Dict[str, str]): Maps base64 chars to key chars
- `decode_map` (Dict[int, str]): Maps key char codes to base64 chars

**Methods:**
- `encode(data: Union[str, bytes], return_bytes: bool = False) -> Union[str, bytes]` - Encode data
- `decode(data: Union[str, bytes], return_bytes: bool = False) -> Union[str, bytes]` - Decode data
- `encode_stream(input_stream, output_stream, chunk_size: int = 8192) -> int` - Stream encode
- `decode_stream(input_stream, output_stream, chunk_size: int = 8192) -> int` - Stream decode
- `encode_iter(data: str, chunk_size: int = 1024) -> Iterator[str]` - Iterative encode
- `decode_iter(data: str, chunk_size: int = 1024) -> Iterator[str]` - Iterative decode
- `verify_roundtrip(test_data: str = "Hello, World! 123") -> bool` - Test encode/decode

**Class Methods:**
- `from_keygenerator(keygen, source: str) -> Encoder` - Create from KeyGenerator

**Exceptions:**
- `EncodingError` - General encoding failure
- `InvalidCharacterError` - Invalid character in encoded text

---

### `xenco.keyfile`

Key file persistence.

#### `KeyFile`

```python
from xenco.keyfile import KeyFile

# Create from components
keyfile = KeyFile(
    encode_map=encode_map,
    decode_map=decode_map,
    source="https://example.com",
    ascii_from=32,
    ascii_to=128
)

# Save
keyfile.save("mykey.xenco")

# Load
loaded = KeyFile.load("mykey.xenco")
```

**Constructor:**
- `encode_map` (Dict[str, str]): Encoding mappings
- `decode_map` (Dict[int, str]): Decoding mappings
- `source` (str): Original source
- `ascii_from` (int): ASCII range start
- `ascii_to` (int): ASCII range end
- `created` (Optional[str]): ISO timestamp

**Methods:**
- `save(filepath: str, pretty: bool = False)` - Save to file
- `to_dict() -> dict` - Convert to dictionary
- `get_decode_map_int() -> Dict[int, str]` - Get decode map with int keys
- `inspect() -> str` - Get human-readable info
- `get_metadata() -> dict` - Get metadata only

**Class Methods:**
- `load(filepath: str, verify: bool = True) -> KeyFile` - Load from file
- `from_keygenerator(keygen, source: str) -> KeyFile` - Create from KeyGenerator

**Exceptions:**
- `KeyFileError` - General key file error
- `KeyFileCorruptedError` - Checksum mismatch
- `KeyFileVersionError` - Incompatible version

---

### `xenco.config`

Configuration management.

#### `Config`

```python
from xenco.config import Config

# Initialize (creates default if not exists)
config = Config()

# Access settings
print(config.ascii_from)  # 32
print(config.http_timeout)  # 30

# Modify settings
config.ascii_from = 40
config.http_timeout = 60
config.save()
```

**Constructor:**
- `config_path` (Optional[str]): Custom config path

**Properties:**
- `ascii_from` (int): Default ASCII range start
- `ascii_to` (int): Default ASCII range end
- `key_directory` (Path): Key storage directory
- `http_timeout` (int): HTTP request timeout
- `http_headers` (Dict[str, str]): HTTP headers
- `auto_save_keys` (bool): Auto-save generated keys
- `pretty_print_keys` (bool): Pretty-print key files
- `progress_indicator` (bool): Show progress indicators

**Methods:**
- `get(key: str, default: Any = None) -> Any` - Get value by dot notation
- `set(key: str, value: Any)` - Set value by dot notation
- `save()` - Save configuration
- `load()` - Load configuration
- `get_key_path(name: str) -> Path` - Get full key path
- `list_keys() -> List[str]` - List available keys
- `reset_to_defaults()` - Reset to defaults
- `to_dict() -> Dict[str, Any]` - Export as dict

**Exceptions:**
- `ConfigError` - Configuration error

---

### `xenco.validator`

Validation utilities.

#### `Validator`

```python
from xenco.validator import Validator, ValidationError

# Validate ASCII range
try:
    Validator.validate_ascii_range(32, 128)
except ValidationError as e:
    print(e)

# Validate source
Validator.validate_source_content(content, 32, 128)

# Validate key mappings
Validator.validate_key_mappings(encode_map, decode_map)
```

**Static Methods:**
- `validate_ascii_range(ascii_from: int, ascii_to: int)` - Validate range
- `validate_source_content(content: str, ascii_from: int, ascii_to: int) -> Set[str]` - Validate source
- `validate_source_type(source: str) -> str` - Classify source type
- `validate_key_mappings(encode_map: dict, decode_map: dict)` - Validate mappings
- `validate_key_file_data(data: dict)` - Validate key file structure
- `validate_encodable_text(text: str, encode_map: dict)` - Validate input
- `validate_decodable_text(text: str, decode_map: dict)` - Validate encoded text
- `validate_file_path(path, **conditions) -> Path` - Validate file path

**Exceptions:**
- `XencoError` - Base exception
- `ValidationError` - Validation failure
- `SourceError` - Source data error
- `KeyError` - Key-related error
- `InputError` - Input data error

---

### `xenco.utils`

File I/O utilities.

```python
from xenco.utils import (
    read_text_file, write_text_file,
    read_binary_file, write_binary_file,
    read_file_chunked, write_file_chunked,
    get_file_info, is_large_file
)

# Simple file operations
content = read_text_file("file.txt")
write_text_file("output.txt", "content")

# Chunked operations
for chunk in read_file_chunked("large.txt"):
    process(chunk)

# File info
info = get_file_info("file.txt")
print(f"Size: {info['size_human']}")
```

**Functions:**
- `read_text_file(filepath, encoding=None, errors="strict") -> str`
- `write_text_file(filepath, content, encoding="utf-8", newline=None) -> int`
- `read_binary_file(filepath) -> bytes`
- `write_binary_file(filepath, content) -> int`
- `read_file_chunked(filepath, chunk_size=8192, encoding="utf-8", progress=False) -> Iterator[str]`
- `write_file_chunked(filepath, chunks, encoding="utf-8", progress=False, expected_size=None) -> int`
- `get_file_info(filepath) -> dict`
- `is_large_file(filepath, threshold=1048576) -> bool`

**Exceptions:**
- `FileIOError` - File operation error
- `EncodingDetectionError` - Encoding detection failure
