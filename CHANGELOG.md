# Changelog

All notable changes to xEnco will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-10-21

### Added
- New `batch` CLI command and `xenco.batch.encode_batch()` API for encoding entire directories
  - `mode="separate"` (default): creates one `.xenco` file next to each original file
  - `mode="one"`: produces a single combined output with length-prefixed file headers
  - Recursive directory scanning with `--no-recursive` option
  - Skips already-encoded `.xenco` files and the key file itself
  - Exclude specific files, directories, or extensions with
    `--exclude-file`, `--exclude-dir`, `--exclude-ext`
  - `decode_combined()` helper to split a combined batch file back into individual files
- Added map hash metadata to key files
  - `encode_map_md5`, `encode_map_crc32`, `decode_map_md5`, `decode_map_crc32`
  - Hashes are deterministic and stored in the key JSON for quick comparison
- New `mix` CLI command and `KeyFile.mix()` API for remixing existing keys
  - `--shift`, `--reverse`, and `--seed` options to change character mappings
  - Produces a different encoding while remaining decodeable with the mixed key
- Directory support in key generation
  - `KeyGenerator` now accepts a directory path as source
  - Reads all readable text files and attempts to ensure their characters are covered
  - `Validator.validate_source_type()` returns `"directory"` for directory paths
- Standalone `main.py` launcher for running the CLI without installing the package

### Changed
- Bumped version to 1.2.0 in `setup.py` and `xenco/__init__.py`
- Updated README.md with `batch`, `mix`, directory key generation, and `main.py` usage
- Test suite updated and expanded for new features
  - 141 tests passing

## [1.1.0] - 2026-07-12

### Added
- New `generate_key()` convenience function for simple one-line key generation
  - Supports URL, file, or text sources
  - Optional output file path with pretty-printed JSON
  - Custom ASCII range parameters
  - Returns KeyFile object when saving, or tuple of mappings when not saving
- Example script `examples/simple_generate.py` demonstrating `generate_key()` usage
- Comprehensive unit tests for `generate_key()` function in `tests/test_keygen.py`

### Changed
- Updated ASCII range default from 32-128 to 32-127 (valid ASCII range is 0-127)
- Fixed base64 padding character (`=`) handling in encoder validation

### Documentation
- Updated README.md with new `generate_key()` examples
- Added API documentation for the convenience function

## [1.0.0] - 2024-01-15

### Added
- Initial release of xEnco
- Dynamic key generation from URLs, files, or text
- Base64-based encoding with custom character mapping
- Bidirectional encoding/decoding
- Key persistence in JSON format with SHA-256 checksums
- CLI with subcommands: `keygen`, `encode`, `decode`, `inspect`
- Python API with KeyGenerator, Encoder, KeyFile classes
- Configuration management with ~/.xenco/config.json
- Comprehensive validation system
- File I/O utilities with chunked reading/writing
- Full test suite with pytest
- Documentation: usage guide, API reference, troubleshooting

### Features
- 65 character mappings (64 base64 + padding)
- Configurable ASCII ranges (default 32-127)
- Content caching for URL sources
- Streaming support for large files
- Progress indicators
- Pretty-printed key files
- Hierarchical exception handling
