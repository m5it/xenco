# xEnco Troubleshooting Guide

## Common Errors and Solutions

### Key Generation Errors

#### "Source contains only X unique characters, but 64 are required"

**Cause:** Your source material doesn't have enough unique characters in the specified ASCII range.

**Solutions:**
1. Use a larger source (longer webpage, bigger file)
2. Expand the ASCII range:
   ```bash
   xenco keygen -s "source" -o key.xenco -f 32 -t 127
   ```
3. Use a source with more character diversity (text with numbers, symbols, etc.)

#### "Failed to fetch URL..."

**Cause:** Network error or invalid URL.

**Solutions:**
1. Check your internet connection
2. Verify the URL is correct and accessible
3. Increase HTTP timeout in config:
   ```python
   from xenco.config import Config
   config = Config()
   config.http_timeout = 60
   config.save()
   ```

### Encoding/Decoding Errors

#### "Text contains characters not in key"

**Cause:** You're trying to decode text with the wrong key file.

**Solutions:**
1. Use the same key file that was used for encoding
2. Verify you have the correct key file
3. Check key file integrity:
   ```bash
   xenco inspect -k key.xenco
   ```

#### "Invalid encoded char..."

**Cause:** The encoded text contains characters not in the key's character set.

**Solutions:**
1. Ensure the encoded text hasn't been modified
2. Check for encoding issues (line endings, BOM markers)
3. Re-encode with the original data

#### "Decoding failed: Incorrect padding"

**Cause:** The encoded text is incomplete or corrupted.

**Solutions:**
1. Verify the entire encoded text was saved/transferred
2. Check for truncation in email or messaging apps
3. Re-encode the original message

### Key File Errors

#### "Key file checksum mismatch"

**Cause:** The key file has been modified or corrupted.

**Solutions:**
1. Regenerate the key from the original source
2. Restore from backup
3. Load with verification disabled (not recommended for production):
   ```python
   keyfile = KeyFile.load("key.xenco", verify=False)
   ```

#### "Key file version X not supported"

**Cause:** The key file was created with a different version of xEnco.

**Solutions:**
1. Update xEnco to the latest version
2. Regenerate the key with your current version

### File I/O Errors

#### "Path is not readable/writable"

**Cause:** Permission denied or file locked.

**Solutions:**
1. Check file permissions:
   ```bash
   ls -la /path/to/file
   ```
2. Run with appropriate permissions
3. Choose a different output directory

#### "Parent directory does not exist"

**Cause:** The output directory doesn't exist.

**Solutions:**
1. Create the directory first:
   ```bash
   mkdir -p /path/to/output
   ```
2. Or let xEnco create it (automatic for most operations)

### Performance Issues

#### Encoding/decoding is slow

**Solutions:**
1. Use streaming for large files:
   ```python
   encoder.encode_stream(input_stream, output_stream)
   ```
2. Adjust chunk size:
   ```python
   encoder.encode_iter(data, chunk_size=4096)
   ```
3. Disable progress indicators for batch operations:
   ```bash
   xenco encode ... -q
   ```

#### Memory usage is high

**Solutions:**
1. Use chunked reading/writing
2. Process files iteratively
3. Clear key generator cache periodically:
   ```python
   keygen.clear_cache()
   ```

## Debug Mode

Enable verbose output to see detailed information:

```bash
xenco encode -i input.txt -k key.xenco -o output.txt -v
```

## Getting Help

If you encounter an issue not covered here:

1. Check the error message carefully
2. Verify your command syntax
3. Test with a simple example first
4. Check the [API documentation](api.md) for detailed usage
