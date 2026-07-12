# Changelog

All notable changes to xEnco will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
