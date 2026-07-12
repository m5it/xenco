"""
xEnco Utilities

Helper functions for file I/O, streaming, and common operations.
"""

import os
import sys
import io
from pathlib import Path
from typing import BinaryIO, Iterator, Optional, TextIO, Union


# Default chunk sizes
DEFAULT_CHUNK_SIZE = 8192  # 8KB for text
LARGE_FILE_THRESHOLD = 1024 * 1024  # 1MB
PROGRESS_UPDATE_INTERVAL = 1024 * 100  # 100KB


class FileIOError(Exception):
    """Exception raised for file I/O errors."""
    pass


class EncodingDetectionError(FileIOError):
    """Exception raised when encoding detection fails."""
    pass


def read_text_file(
    filepath: Union[str, Path],
    encoding: Optional[str] = None,
    errors: str = "strict"
) -> str:
    """
    Read text file with optional encoding detection.
    
    Args:
        filepath: Path to file
        encoding: Encoding to use (None for auto-detect, defaults to UTF-8)
        errors: Error handling ('strict', 'ignore', 'replace')
    
    Returns:
        File contents as string
    
    Raises:
        FileIOError: If file cannot be read
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileIOError(f"File not found: {filepath}")
    
    if not filepath.is_file():
        raise FileIOError(f"Not a file: {filepath}")
    
    # Default to UTF-8 if not specified
    if encoding is None:
        encoding = "utf-8"
    
    try:
        with open(filepath, "r", encoding=encoding, errors=errors) as f:
            return f.read()
    except UnicodeDecodeError as e:
        raise EncodingDetectionError(f"Failed to decode {filepath} with {encoding}: {e}")
    except Exception as e:
        raise FileIOError(f"Failed to read {filepath}: {e}")


def read_binary_file(filepath: Union[str, Path]) -> bytes:
    """
    Read file as binary data.
    
    Args:
        filepath: Path to file
    
    Returns:
        File contents as bytes
    
    Raises:
        FileIOError: If file cannot be read
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileIOError(f"File not found: {filepath}")
    
    try:
        with open(filepath, "rb") as f:
            return f.read()
    except Exception as e:
        raise FileIOError(f"Failed to read {filepath}: {e}")


def write_text_file(
    filepath: Union[str, Path],
    content: str,
    encoding: str = "utf-8",
    newline: Optional[str] = None
) -> int:
    """
    Write text to file with proper encoding and line ending handling.
    
    Args:
        filepath: Path to file
        content: Text content to write
        encoding: Encoding to use
        newline: Line ending control (None=platform default, '', '\n', '\r\n')
    
    Returns:
        Number of characters written
    
    Raises:
        FileIOError: If file cannot be written
    """
    filepath = Path(filepath)
    
    try:
        # Ensure parent directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, "w", encoding=encoding, newline=newline) as f:
            return f.write(content)
    except Exception as e:
        raise FileIOError(f"Failed to write {filepath}: {e}")


def write_binary_file(filepath: Union[str, Path], content: bytes) -> int:
    """
    Write binary data to file.
    
    Args:
        filepath: Path to file
        content: Binary content to write
    
    Returns:
        Number of bytes written
    
    Raises:
        FileIOError: If file cannot be written
    """
    filepath = Path(filepath)
    
    try:
        # Ensure parent directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, "wb") as f:
            return f.write(content)
    except Exception as e:
        raise FileIOError(f"Failed to write {filepath}: {e}")


def read_file_chunked(
    filepath: Union[str, Path],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    encoding: Optional[str] = "utf-8",
    progress: bool = False
) -> Iterator[str]:
    """
    Read file in chunks, yielding text segments.
    
    Args:
        filepath: Path to file
        chunk_size: Size of chunks to read
        encoding: Text encoding (None for binary)
        progress: Show progress indicator
    
    Yields:
        Text chunks
    
    Raises:
        FileIOError: If file cannot be read
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileIOError(f"File not found: {filepath}")
    
    file_size = filepath.stat().st_size
    bytes_read = 0
    
    try:
        if encoding:
            # Text mode
            with open(filepath, "r", encoding=encoding) as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    bytes_read += len(chunk.encode(encoding))
                    
                    if progress and file_size > LARGE_FILE_THRESHOLD:
                        _show_progress(bytes_read, file_size, filepath.name)
                    
                    yield chunk
        else:
            # Binary mode - yield as strings for consistency
            with open(filepath, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    bytes_read += len(chunk)
                    
                    if progress and file_size > LARGE_FILE_THRESHOLD:
                        _show_progress(bytes_read, file_size, filepath.name)
                    
                    yield chunk.decode("utf-8", errors="replace")
        
        if progress and file_size > LARGE_FILE_THRESHOLD:
            print(f"\r{filepath.name}: Complete{' ' * 20}", file=sys.stderr)
            
    except Exception as e:
        raise FileIOError(f"Failed to read {filepath}: {e}")


def write_file_chunked(
    filepath: Union[str, Path],
    chunks: Iterator[str],
    encoding: str = "utf-8",
    progress: bool = False,
    expected_size: Optional[int] = None
) -> int:
    """
    Write chunks to file.
    
    Args:
        filepath: Path to file
        chunks: Iterator yielding text chunks
        encoding: Text encoding
        progress: Show progress indicator
        expected_size: Expected total size for progress calculation
    
    Returns:
        Total bytes written
    
    Raises:
        FileIOError: If file cannot be written
    """
    filepath = Path(filepath)
    bytes_written = 0
    
    try:
        # Ensure parent directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, "w", encoding=encoding) as f:
            for chunk in chunks:
                chunk_bytes = chunk.encode(encoding)
                f.write(chunk)
                bytes_written += len(chunk_bytes)
                
                if progress and expected_size and bytes_written % PROGRESS_UPDATE_INTERVAL < chunk_size:
                    _show_progress(bytes_written, expected_size, filepath.name)
        
        if progress and expected_size:
            print(f"\r{filepath.name}: Complete{' ' * 20}", file=sys.stderr)
        
        return bytes_written
        
    except Exception as e:
        raise FileIOError(f"Failed to write {filepath}: {e}")


def _show_progress(current: int, total: int, name: str) -> None:
    """Display progress indicator."""
    percent = (current / total) * 100
    bar_length = 30
    filled = int(bar_length * current / total)
    bar = "=" * filled + "-" * (bar_length - filled)
    print(f"\r{name}: [{bar}] {percent:.1f}%", end="", file=sys.stderr, flush=True)


def is_large_file(filepath: Union[str, Path], threshold: int = LARGE_FILE_THRESHOLD) -> bool:
    """
    Check if file is considered large.
    
    Args:
        filepath: Path to file
        threshold: Size threshold in bytes
    
    Returns:
        True if file size >= threshold
    """
    try:
        return Path(filepath).stat().st_size >= threshold
    except:
        return False


def get_file_info(filepath: Union[str, Path]) -> dict:
    """
    Get file information.
    
    Args:
        filepath: Path to file
    
    Returns:
        Dictionary with file info
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        return {"exists": False, "path": str(filepath)}
    
    stat = filepath.stat()
    
    return {
        "exists": True,
        "path": str(filepath.absolute()),
        "size": stat.st_size,
        "size_human": _format_size(stat.st_size),
        "is_large": stat.st_size >= LARGE_FILE_THRESHOLD,
        "modified": stat.st_mtime
    }


def _format_size(size_bytes: int) -> str:
    """Format byte size to human readable."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def safe_read_stdin() -> str:
    """
    Safely read all data from stdin.
    
    Returns:
        stdin contents as string
    
    Raises:
        FileIOError: If read fails
    """
    try:
        return sys.stdin.read()
    except Exception as e:
        raise FileIOError(f"Failed to read stdin: {e}")


def safe_write_stdout(data: str, add_newline: bool = True) -> None:
    """
    Safely write data to stdout.
    
    Args:
        data: Data to write
        add_newline: Add newline if data doesn't end with one
    
    Raises:
        FileIOError: If write fails
    """
    try:
        sys.stdout.write(data)
        if add_newline and not data.endswith('\n'):
            sys.stdout.write('\n')
        sys.stdout.flush()
    except Exception as e:
        raise FileIOError(f"Failed to write stdout: {e}")


def copy_file_preserve_metadata(
    src: Union[str, Path],
    dst: Union[str, Path],
    progress: bool = False
) -> None:
    """
    Copy file while preserving metadata and handling large files.
    
    Args:
        src: Source file path
        dst: Destination file path
        progress: Show progress indicator
    
    Raises:
        FileIOError: If copy fails
    """
    src_path = Path(src)
    dst_path = Path(dst)
    
    if not src_path.exists():
        raise FileIOError(f"Source file not found: {src}")
    
    try:
        # Use chunked copy for large files
        if is_large_file(src_path):
            total_size = src_path.stat().st_size
            bytes_copied = 0
            
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(src_path, "rb") as fsrc:
                with open(dst_path, "wb") as fdst:
                    while True:
                        chunk = fsrc.read(DEFAULT_CHUNK_SIZE)
                        if not chunk:
                            break
                        fdst.write(chunk)
                        bytes_copied += len(chunk)
                        
                        if progress:
                            _show_progress(bytes_copied, total_size, src_path.name)
            
            if progress:
                print(f"\r{src_path.name}: Complete{' ' * 20}", file=sys.stderr)
        else:
            # Simple copy for small files
            import shutil
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            
    except Exception as e:
        raise FileIOError(f"Failed to copy {src} to {dst}: {e}")
