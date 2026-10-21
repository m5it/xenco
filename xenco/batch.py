"""
xEnco Batch Encoding

Encode multiple files from a directory in one operation.

Modes:
    one       - Encode all files into a single output file with headers
                so each file can be recovered later.
    separate  - Encode each file individually, creating a matching
                ``.xenco`` file next to the original.
"""

import os
import fnmatch
from pathlib import Path
from typing import Collection, Dict, List, Optional, Set, Tuple, Union

from .encoder import Encoder
from .keyfile import KeyFile, KeyFileError


# Header used to delimit files in "mode=one" output.
# Format: b"XENCO_FILE\x1f<relative-path>\x1f<content-length>\n"
_FILE_HEADER_PREFIX = b"XENCO_FILE\x1f"
_FILE_HEADER_SUFFIX = b"\n"
_FILE_FIELD_SEP = b"\x1f"


class BatchEncodingError(Exception):
    """Exception raised for batch encoding operations."""
    pass


def _compile_excludes(
    directory: Path,
    exclude_files: Optional[Collection[str]] = None,
    exclude_dirs: Optional[Collection[str]] = None,
    exclude_extensions: Optional[Collection[str]] = None,
) -> Tuple[Set[str], Set[str], Set[str]]:
    """
    Normalize exclude lists to absolute paths and lowercase extension/suffix sets.

    Patterns are resolved relative to ``directory``. Bare file or directory names
    are matched anywhere in the tree.
    """
    exclude_files = set(exclude_files or ())
    exclude_dirs = set(exclude_dirs or ())
    exclude_extensions = set(exclude_extensions or ())

    resolved_files: Set[str] = set()
    for item in exclude_files:
        path = Path(item)
        if not path.is_absolute():
            path = directory / path
        resolved_files.add(str(path.resolve()))
        # Also accept bare names anywhere in the tree
        resolved_files.add(path.name)

    resolved_dirs: Set[str] = set()
    for item in exclude_dirs:
        path = Path(item)
        if not path.is_absolute():
            path = directory / path
        resolved_dirs.add(str(path.resolve()))
        resolved_dirs.add(path.name)

    normalized_extensions: Set[str] = set()
    for ext in exclude_extensions:
        ext = ext.lower()
        if not ext.startswith("."):
            ext = f".{ext}"
        normalized_extensions.add(ext)

    return resolved_files, resolved_dirs, normalized_extensions


def _is_excluded(
    filepath: Path,
    root_dir: Path,
    exclude_files: Set[str],
    exclude_dirs: Set[str],
    exclude_extensions: Set[str],
) -> bool:
    """Return True if a file should be skipped based on exclude rules."""
    # File by absolute path or name
    if str(filepath.resolve()) in exclude_files or filepath.name in exclude_files:
        return True

    # Extension check
    if filepath.suffix.lower() in exclude_extensions:
        return True

    # Directory check: if any part of the relative path is an excluded directory
    try:
        rel_parts = filepath.resolve().relative_to(root_dir.resolve()).parts
    except ValueError:
        rel_parts = ()

    for part in rel_parts[:-1]:
        if part in exclude_dirs:
            return True

    return False


def find_files(
    directory: Union[str, Path],
    recursive: bool = True,
    skip_suffixes: Optional[Tuple[str, ...]] = None,
    exclude_files: Optional[Collection[str]] = None,
    exclude_dirs: Optional[Collection[str]] = None,
    exclude_extensions: Optional[Collection[str]] = None,
) -> List[Path]:
    """
    Find all regular files in a directory that should be encoded.

    Args:
        directory: Root directory to scan
        recursive: If True, also walk into subdirectories
        skip_suffixes: File suffixes to skip (e.g., output suffixes to avoid
                       re-encoding already encoded files)
        exclude_files: File paths or names to skip. Relative paths are resolved
                      from ``directory``. Bare names match anywhere in the tree.
        exclude_dirs: Directory paths or names to skip entirely. Relative paths
                      are resolved from ``directory``. Bare names match anywhere.
        exclude_extensions: File extensions to skip, with or without leading dot.

    Returns:
        Sorted list of absolute file paths

    Raises:
        BatchEncodingError: If directory is invalid
    """
    directory = Path(directory).resolve()

    if not directory.exists():
        raise BatchEncodingError(f"Directory not found: {directory}")
    if not directory.is_dir():
        raise BatchEncodingError(f"Not a directory: {directory}")

    skip_suffixes = skip_suffixes or (".xenco",)

    ex_files, ex_dirs, ex_extensions = _compile_excludes(
        directory, exclude_files, exclude_dirs, exclude_extensions
    )

    files: List[Path] = []

    if recursive:
        for root, dirs, filenames in os.walk(directory):
            root_path = Path(root)

            # Skip excluded directories while walking
            dirs[:] = [
                d for d in dirs
                if d not in ex_dirs and str((root_path / d).resolve()) not in ex_dirs
            ]

            for name in filenames:
                filepath = root_path / name
                if not filepath.is_file():
                    continue
                if any(str(filepath).endswith(suffix) for suffix in skip_suffixes):
                    continue
                if _is_excluded(filepath, directory, ex_files, ex_dirs, ex_extensions):
                    continue
                files.append(filepath)
    else:
        for entry in sorted(os.listdir(directory)):
            filepath = directory / entry
            if not filepath.is_file():
                continue
            if any(str(filepath).endswith(suffix) for suffix in skip_suffixes):
                continue
            if _is_excluded(filepath, directory, ex_files, ex_dirs, ex_extensions):
                continue
            files.append(filepath)

    return sorted(files)


def _make_file_header(relative_path: str, content_length: int) -> bytes:
    """Create a binary header for one file in combined output."""
    return (
        _FILE_HEADER_PREFIX
        + relative_path.encode("utf-8")
        + _FILE_FIELD_SEP
        + str(content_length).encode("utf-8")
        + _FILE_HEADER_SUFFIX
    )


def _build_combined_data(directory: Path, files: List[Path]) -> bytes:
    """
    Combine all files into one byte stream with length-prefixed headers.

    The format is self-describing, so the combined output can be decoded
    and split back into individual files.
    """
    parts: List[bytes] = []
    for filepath in files:
        relative_path = filepath.relative_to(directory).as_posix()
        try:
            content = filepath.read_bytes()
        except Exception as e:
            raise BatchEncodingError(f"Failed to read {filepath}: {e}")

        parts.append(_make_file_header(relative_path, len(content)))
        parts.append(content)

    return b"".join(parts)


def encode_batch(
    directory: Union[str, Path],
    key_path: Union[str, Path],
    output: Optional[Union[str, Path]] = None,
    mode: str = "separate",
    recursive: bool = True,
    overwrite: bool = False,
    suffix: str = ".xenco",
    quiet: bool = False,
    exclude_files: Optional[Collection[str]] = None,
    exclude_dirs: Optional[Collection[str]] = None,
    exclude_extensions: Optional[Collection[str]] = None,
    dry_run: bool = False,
) -> Dict[str, Union[int, List[str], str]]:
    """
    Encode all files in a directory.

    Args:
        directory: Directory to scan
        key_path: Path to key file to use
        output: Output file for mode="one" or output directory for mode="separate".
                If not provided for mode="separate", encoded files are placed
                next to the originals.
        mode: ``"one"`` for a single combined output, ``"separate"`` for
              one output file per input file
        recursive: Whether to walk into subdirectories
        overwrite: Whether to overwrite existing output files
        suffix: Suffix appended to each output file in mode="separate"
        quiet: If True, suppress progress output
        exclude_files: File paths or names to skip
        exclude_dirs: Directory paths or names to skip
        exclude_extensions: File extensions to skip
        dry_run: If True, only report what would be done; no files are written

    Returns:
        Dictionary with encoding results:
            {
                "mode": "one" or "separate",
                "directory": str,
                "output": str,
                "files": list of relative paths encoded,
                "count": number of files encoded,
                "bytes_written": total bytes written,
                "dry_run": True or False
            }

    Raises:
        BatchEncodingError: If encoding fails
        KeyFileError: If the key file cannot be loaded
    """
    directory = Path(directory).resolve()
    if not directory.is_dir():
        raise BatchEncodingError(f"Not a directory: {directory}")

    # Load key and create encoder
    keyfile = KeyFile.load(str(key_path))
    encoder = Encoder(keyfile.encode_map, keyfile.get_decode_map_int())

    # Find files, also skipping the key file if it happens to live inside the tree
    skip_suffixes = (suffix, ".xenco")
    files = find_files(
        directory,
        recursive=recursive,
        skip_suffixes=skip_suffixes,
        exclude_files=exclude_files,
        exclude_dirs=exclude_dirs,
        exclude_extensions=exclude_extensions,
    )
    key_path_resolved = Path(key_path).resolve()
    files = [f for f in files if f.resolve() != key_path_resolved]

    if not files:
        raise BatchEncodingError("No encodable files found in directory")

    if dry_run:
        # Report what would be created without writing anything
        if mode == "one":
            output_path = Path(output) if output else Path(directory) / f"combined{suffix}"
            output_desc = str(output_path)
        else:
            output_dir = Path(output) if output else directory
            output_desc = str(output_dir)

        if not quiet:
            print(f"DRY RUN: would encode {len(files)} file(s)")
            print(f"  Mode: {mode}")
            print(f"  Output: {output_desc}")
            print("  Files:")
            for f in files:
                print(f"    {f.relative_to(directory).as_posix()}")

        return {
            "mode": mode,
            "directory": str(directory),
            "output": output_desc,
            "files": [f.relative_to(directory).as_posix() for f in files],
            "count": len(files),
            "bytes_written": 0,
            "dry_run": True,
        }

    if mode == "one":
        if output is None:
            raise BatchEncodingError("Output path is required for mode='one'")

        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_path.exists() and not overwrite:
            raise BatchEncodingError(f"Output file already exists: {output_path}")

        combined = _build_combined_data(directory, files)
        encoded = encoder.encode(combined, return_bytes=False)
        output_path.write_text(encoded, encoding="utf-8")

        result = {
            "mode": "one",
            "directory": str(directory),
            "output": str(output_path),
            "files": [f.relative_to(directory).as_posix() for f in files],
            "count": len(files),
            "bytes_written": len(encoded.encode("utf-8")),
            "dry_run": False,
        }

    elif mode == "separate":
        output_dir = Path(output) if output else None
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)

        encoded_files: List[str] = []
        total_bytes = 0

        for filepath in files:
            try:
                content = filepath.read_bytes()
            except Exception as e:
                raise BatchEncodingError(f"Failed to read {filepath}: {e}")

            encoded = encoder.encode(content, return_bytes=False)

            if output_dir:
                relative = filepath.relative_to(directory)
                out_path = output_dir / relative
                out_path = out_path.with_name(out_path.name + suffix)
            else:
                out_path = filepath.with_name(filepath.name + suffix)

            out_path.parent.mkdir(parents=True, exist_ok=True)

            if out_path.exists() and not overwrite:
                raise BatchEncodingError(f"Output file already exists: {out_path}")

            out_path.write_text(encoded, encoding="utf-8")

            relative_out = out_path.relative_to(directory).as_posix() if output_dir is None else str(out_path)
            encoded_files.append(relative_out)
            total_bytes += len(encoded.encode("utf-8"))

        result = {
            "mode": "separate",
            "directory": str(directory),
            "output": str(output_dir) if output_dir else "same-as-source",
            "files": [f.relative_to(directory).as_posix() for f in files],
            "count": len(files),
            "bytes_written": total_bytes,
            "dry_run": False,
        }

    else:
        raise BatchEncodingError(f"Unknown mode: {mode!r}. Use 'one' or 'separate'.")

    if not quiet:
        print(f"Batch encoded {result['count']} file(s)")
        print(f"  Mode: {result['mode']}")
        print(f"  Output: {result['output']}")

    return result


def decode_combined(
    encoded_text: str,
    key_path: Union[str, Path]
) -> List[Tuple[str, bytes]]:
    """
    Decode a combined "mode=one" batch encoding back into individual files.

    Args:
        encoded_text: Combined encoded text
        key_path: Path to key file

    Returns:
        List of (relative_path, content_bytes) tuples
    """
    keyfile = KeyFile.load(str(key_path))
    encoder = Encoder(keyfile.encode_map, keyfile.get_decode_map_int())

    combined_bytes = encoder.decode(encoded_text, return_bytes=True)
    results: List[Tuple[str, bytes]] = []
    offset = 0

    while offset < len(combined_bytes):
        # Find end of header line
        newline_pos = combined_bytes.find(_FILE_HEADER_SUFFIX, offset)
        if newline_pos == -1:
            raise BatchEncodingError("Malformed combined output: missing header")

        header = combined_bytes[offset:newline_pos]
        if not header.startswith(_FILE_HEADER_PREFIX):
            raise BatchEncodingError("Malformed combined output: invalid header")

        body = header[len(_FILE_HEADER_PREFIX):]
        fields = body.split(_FILE_FIELD_SEP)
        if len(fields) != 2:
            raise BatchEncodingError("Malformed combined output: bad header format")

        relative_path = fields[0].decode("utf-8")
        content_length = int(fields[1].decode("utf-8"))

        content_start = newline_pos + len(_FILE_HEADER_SUFFIX)
        content_end = content_start + content_length
        if content_end > len(combined_bytes):
            raise BatchEncodingError("Malformed combined output: content truncated")

        results.append((relative_path, combined_bytes[content_start:content_end]))
        offset = content_end

    return results
