"""
xEnco Batch Encoding/Decoding

Encode or decode multiple files from a directory in one operation.

Encoding modes:
    one       - Encode all files into a single output file with headers
                so each file can be recovered later.
    separate  - Encode each file individually, creating a matching
                ``.xenco`` file next to the original.

Decoding modes:
    one       - Decode a single combined file back into the original
                directory structure.
    separate  - Decode all ``.xenco`` files in a directory back to their
                original names.
"""

import os
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
    match_suffixes: Optional[Tuple[str, ...]] = None,
    exclude_files: Optional[Collection[str]] = None,
    exclude_dirs: Optional[Collection[str]] = None,
    exclude_extensions: Optional[Collection[str]] = None,
) -> List[Path]:
    """
    Find all regular files in a directory.

    Args:
        directory: Root directory to scan
        recursive: If True, also walk into subdirectories
        skip_suffixes: File suffixes to skip (e.g., output suffixes to avoid
                       re-encoding already encoded files)
        match_suffixes: If provided, only return files that end with one of
                        these suffixes. Useful for finding ``.xenco`` files to
                        decode.
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

    skip_suffixes = skip_suffixes or ()
    match_suffixes = match_suffixes or ()
    # Keep the historical default: skip .xenco when neither skip nor match is provided
    if not skip_suffixes and not match_suffixes:
        skip_suffixes = (".xenco",)

    ex_files, ex_dirs, ex_extensions = _compile_excludes(
        directory, exclude_files, exclude_dirs, exclude_extensions
    )

    files: List[Path] = []

    def _include(filepath: Path) -> bool:
        if not filepath.is_file():
            return False
        if any(str(filepath).endswith(suffix) for suffix in skip_suffixes):
            return False
        if match_suffixes and not any(str(filepath).endswith(suffix) for suffix in match_suffixes):
            return False
        if _is_excluded(filepath, directory, ex_files, ex_dirs, ex_extensions):
            return False
        return True

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
                if _include(filepath):
                    files.append(filepath)
    else:
        for entry in sorted(os.listdir(directory)):
            filepath = directory / entry
            if _include(filepath):
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


def decode_batch(
    directory: Union[str, Path],
    key_path: Union[str, Path],
    input_path: Optional[Union[str, Path]] = None,
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
    Decode all encoded files in a directory or a single combined file.

    Args:
        directory: Directory where decoded files should be written. For
                   ``mode="separate"`` this is also scanned for ``.xenco``
                   files when ``input_path`` is not given and ``output`` is not
                   set.
        key_path: Path to key file to use
        input_path: For ``mode="one"``, the combined encoded file. For
                    ``mode="separate"``, an alternate source directory of
                    ``.xenco`` files.
        output: Alias for ``directory`` (used by the CLI); if provided, it
                overrides ``directory`` as the destination directory.
        mode: ``"one"`` to decode a single combined file, ``"separate"`` to
              decode each ``.xenco`` file individually
        recursive: Whether to walk into subdirectories in separate mode
        overwrite: Whether to overwrite existing decoded files
        suffix: Suffix that identifies encoded files in separate mode
        quiet: If True, suppress progress output
        exclude_files: File paths or names to skip when scanning for encoded files
        exclude_dirs: Directory paths or names to skip when scanning
        exclude_extensions: File extensions to skip when scanning
        dry_run: If True, only report what would be done; no files are written

    Returns:
        Dictionary with decoding results:
            {
                "mode": "one" or "separate",
                "directory": str,
                "input": str,
                "output": str,
                "files": list of relative paths decoded,
                "count": number of files decoded,
                "bytes_written": total bytes written,
                "dry_run": True or False
            }

    Raises:
        BatchEncodingError: If decoding fails
        KeyFileError: If the key file cannot be loaded
    """
    directory = Path(directory).resolve()
    if output:
        directory = Path(output).resolve()
    directory.mkdir(parents=True, exist_ok=True)

    if not directory.is_dir():
        raise BatchEncodingError(f"Not a directory: {directory}")

    # Load key and create encoder
    keyfile = KeyFile.load(str(key_path))
    encoder = Encoder(keyfile.encode_map, keyfile.get_decode_map_int())

    if mode == "one":
        source_file = Path(input_path) if input_path else None
        if source_file is None:
            raise BatchEncodingError("Input path is required for mode='one'")
        if not source_file.is_file():
            raise BatchEncodingError(f"Input file not found: {source_file}")

        encoded_text = source_file.read_text(encoding="utf-8")
        decoded_files = decode_combined(encoded_text, str(key_path))

        if dry_run:
            if not quiet:
                print(f"DRY RUN: would decode {len(decoded_files)} file(s)")
                print(f"  Mode: one")
                print(f"  Input: {source_file}")
                print(f"  Output directory: {directory}")
                print("  Files:")
                for relative_path, _ in decoded_files:
                    print(f"    {relative_path}")
            return {
                "mode": "one",
                "directory": str(directory),
                "input": str(source_file),
                "output": str(directory),
                "files": [relative_path for relative_path, _ in decoded_files],
                "count": len(decoded_files),
                "bytes_written": 0,
                "dry_run": True,
            }

        total_bytes = 0
        decoded_paths: List[str] = []

        for relative_path, content in decoded_files:
            relative_path = relative_path.lstrip("/")
            out_path = directory / relative_path
            out_path.parent.mkdir(parents=True, exist_ok=True)

            if out_path.exists() and not overwrite:
                raise BatchEncodingError(f"Output file already exists: {out_path}")

            out_path.write_bytes(content)
            decoded_paths.append(relative_path)
            total_bytes += len(content)

        result = {
            "mode": "one",
            "directory": str(directory),
            "input": str(source_file),
            "output": str(directory),
            "files": decoded_paths,
            "count": len(decoded_paths),
            "bytes_written": total_bytes,
            "dry_run": False,
        }

    elif mode == "separate":
        source_dir = Path(input_path).resolve() if input_path else directory
        if source_dir.resolve() == directory.resolve() and output:
            raise BatchEncodingError(
                "Source and output directory are the same. "
                "Use a different input directory or omit --output."
            )
        if not source_dir.is_dir():
            raise BatchEncodingError(f"Source directory not found: {source_dir}")

        files = find_files(
            source_dir,
            recursive=recursive,
            match_suffixes=(suffix,),
            exclude_files=exclude_files,
            exclude_dirs=exclude_dirs,
            exclude_extensions=exclude_extensions,
        )
        key_path_resolved = Path(key_path).resolve()
        files = [f for f in files if f.resolve() != key_path_resolved]

        if not files:
            raise BatchEncodingError(f"No decodable files found in {source_dir}")

        if dry_run:
            if not quiet:
                print(f"DRY RUN: would decode {len(files)} file(s)")
                print(f"  Mode: separate")
                print(f"  Source: {source_dir}")
                print(f"  Output directory: {directory}")
                print("  Files:")
                for f in files:
                    print(f"    {f.relative_to(source_dir).as_posix()}")
            return {
                "mode": "separate",
                "directory": str(directory),
                "input": str(source_dir),
                "output": str(directory),
                "files": [f.relative_to(source_dir).as_posix() for f in files],
                "count": len(files),
                "bytes_written": 0,
                "dry_run": True,
            }

        total_bytes = 0
        decoded_paths: List[str] = []

        for filepath in files:
            try:
                encoded_text = filepath.read_text(encoding="utf-8")
            except Exception as e:
                raise BatchEncodingError(f"Failed to read {filepath}: {e}")

            try:
                content = encoder.decode(encoded_text, return_bytes=True)
            except Exception as e:
                raise BatchEncodingError(f"Failed to decode {filepath}: {e}")

            relative = filepath.relative_to(source_dir)
            out_path = directory / relative
            if str(out_path).endswith(suffix):
                out_path = out_path.with_name(out_path.name[: -len(suffix)])

            out_path.parent.mkdir(parents=True, exist_ok=True)

            if out_path.exists() and not overwrite:
                raise BatchEncodingError(f"Output file already exists: {out_path}")

            out_path.write_bytes(content)
            decoded_paths.append(relative.as_posix())
            total_bytes += len(content)

        result = {
            "mode": "separate",
            "directory": str(directory),
            "input": str(source_dir),
            "output": str(directory),
            "files": decoded_paths,
            "count": len(decoded_paths),
            "bytes_written": total_bytes,
            "dry_run": False,
        }

    else:
        raise BatchEncodingError(f"Unknown mode: {mode!r}. Use 'one' or 'separate'.")

    if not quiet:
        print(f"Batch decoded {result['count']} file(s)")
        print(f"  Mode: {result['mode']}")
        print(f"  Output directory: {result['output']}")

    return result
