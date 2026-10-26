"""
xEnco Command Line Interface

Main entry point for the xenco CLI tool.
"""

import sys
import argparse
from pathlib import Path

from . import __version__
from .keygen import KeyGenerator, InsufficientSourceError
from .encoder import Encoder
from .keyfile import KeyFile, KeyFileError
from .config import Config
from .utils import read_text_file, write_text_file
from .batch import encode_batch, decode_batch, BatchEncodingError


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog="xenco",
        description="Text Encoder/Decoder with Dynamic Key Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  xenco keygen -s "https://example.com" -o key.xenco
  echo "message" | xenco encode -k key.xenco
  xenco decode -i encoded.txt -k key.xenco -o decoded.txt
        """
    )
    
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress non-error output"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # keygen command
    keygen_parser = subparsers.add_parser(
        "keygen",
        help="Generate a new key from a source"
    )
    keygen_parser.add_argument(
        "-s", "--source",
        required=True,
        help="Source data (URL, file path, or text)"
    )
    keygen_parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output key file path"
    )
    keygen_parser.add_argument(
        "-f", "--from",
        type=int,
        default=32,
        dest="ascii_from",
        help="ASCII range start (default: 32)"
    )
    keygen_parser.add_argument(
        "-t", "--to",
        type=int,
        default=127,
        dest="ascii_to",
        help="ASCII range end (default: 127)"
    )
    keygen_parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output"
    )
    
    # encode command
    encode_parser = subparsers.add_parser(
        "encode",
        help="Encode text using a key"
    )
    encode_parser.add_argument(
        "-k", "--key",
        required=True,
        help="Key file to use"
    )
    encode_parser.add_argument(
        "-i", "--input",
        help="Input file (default: stdin)"
    )
    encode_parser.add_argument(
        "-o", "--output",
        help="Output file (default: stdout)"
    )
    encode_parser.add_argument(
        "-N", "--dry-run",
        action="store_true",
        help="Print encoded data to stdout but do not write any output file"
    )

    # decode command
    decode_parser = subparsers.add_parser(
        "decode",
        help="Decode text using a key"
    )
    decode_parser.add_argument(
        "-k", "--key",
        required=True,
        help="Key file to use"
    )
    decode_parser.add_argument(
        "-i", "--input",
        help="Input file (default: stdin)"
    )
    decode_parser.add_argument(
        "-o", "--output",
        help="Output file (default: stdout)"
    )
    
    # inspect command
    inspect_parser = subparsers.add_parser(
        "inspect",
        help="Inspect a key file"
    )
    inspect_parser.add_argument(
        "-k", "--key",
        required=True,
        help="Key file to inspect"
    )
    inspect_parser.add_argument(
        "--metadata",
        action="store_true",
        help="Show only metadata"
    )

    # mix command
    mix_parser = subparsers.add_parser(
        "mix",
        help="Create a remixed key from an existing key"
    )
    mix_parser.add_argument(
        "-k", "--key",
        required=True,
        help="Input key file to remix"
    )
    mix_parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output key file path"
    )
    mix_parser.add_argument(
        "--shift",
        type=int,
        default=None,
        help="Rotate source character positions by N"
    )
    mix_parser.add_argument(
        "--reverse",
        action="store_true",
        help="Reverse source character positions"
    )
    mix_parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Deterministically shuffle source characters with a seed"
    )
    mix_parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output"
    )

    # batch command
    batch_parser = subparsers.add_parser(
        "batch",
        help="Encode or decode all files in a directory"
    )
    batch_parser.add_argument(
        "--decode",
        action="store_true",
        help="Decode instead of encode"
    )
    batch_parser.add_argument(
        "-d", "--directory",
        required=True,
        help="Directory containing files to encode/decode, or output directory when decoding"
    )
    batch_parser.add_argument(
        "-k", "--key",
        required=True,
        help="Key file to use"
    )
    batch_parser.add_argument(
        "-i", "--input",
        default=None,
        help="Input file for decode mode=one, or source directory for decode mode=separate"
    )
    batch_parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output file for encode mode=one, output directory for encode/decode mode=separate (default: same as source)"
    )
    batch_parser.add_argument(
        "-m", "--mode",
        choices=["one", "separate"],
        default="separate",
        help="Batch mode: one combined output or separate files (default: separate)"
    )
    batch_parser.add_argument(
        "--recursive",
        action="store_true",
        default=True,
        help="Walk into subdirectories (default: True)"
    )
    batch_parser.add_argument(
        "--no-recursive",
        action="store_true",
        default=False,
        help="Do not walk into subdirectories"
    )
    batch_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files"
    )
    batch_parser.add_argument(
        "--suffix",
        default=".xenco",
        help="Output suffix for mode=separate (default: .xenco)"
    )
    batch_parser.add_argument(
        "--exclude-file",
        action="append",
        default=[],
        help="File path or name to exclude (can be repeated)"
    )
    batch_parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help="Directory path or name to exclude (can be repeated)"
    )
    batch_parser.add_argument(
        "--exclude-ext",
        action="append",
        default=[],
        help="File extension to exclude, with or without leading dot (can be repeated)"
    )
    batch_parser.add_argument(
        "-N", "--dry-run",
        action="store_true",
        help="List files that would be encoded/decoded and print what would be created, without writing anything"
    )

    return parser


def cmd_keygen(args) -> int:
    """Execute keygen command."""
    try:
        keygen = KeyGenerator(args.ascii_from, args.ascii_to)
        keyfile = KeyFile.from_keygenerator(keygen, args.source)
        keyfile.save(args.output, pretty=args.pretty)
        
        if not args.quiet:
            info = keyfile.get_metadata()
            print(f"Key generated: {args.output}")
            print(f"  Source: {info['source']}")
            print(f"  ASCII range: {info['ascii_from']}-{info['ascii_to']}")
            print(f"  Mappings: {info['mapping_count']}")
        
        return 0
        
    except InsufficientSourceError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error generating key: {e}", file=sys.stderr)
        return 1


def cmd_encode(args) -> int:
    """Execute encode command."""
    try:
        # Load key
        keyfile = KeyFile.load(args.key)
        encoder = Encoder(keyfile.encode_map, keyfile.get_decode_map_int())
        
        # Read input
        if args.input:
            text = read_text_file(args.input)
        else:
            text = sys.stdin.read()
        
        # Encode
        encoded = encoder.encode(text)

        # Dry run prints encoded data without writing any file
        if args.dry_run:
            print(encoded, end='')
            return 0

        # Write output
        if args.output:
            write_text_file(args.output, encoded)
            if not args.quiet:
                print(f"Encoded to: {args.output}")
        else:
            print(encoded, end='')

        return 0
        
    except KeyFileError as e:
        print(f"Key error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error encoding: {e}", file=sys.stderr)
        return 1


def cmd_decode(args) -> int:
    """Execute decode command."""
    try:
        # Load key
        keyfile = KeyFile.load(args.key)
        encoder = Encoder(keyfile.encode_map, keyfile.get_decode_map_int())
        
        # Read input
        if args.input:
            text = read_text_file(args.input)
        else:
            text = sys.stdin.read()
        
        # Decode
        decoded = encoder.decode(text)
        
        # Write output
        if args.output:
            if args.output == "-":
                print(decoded, end='')
            else:
                write_text_file(args.output, decoded)
                if not args.quiet:
                    print(f"Decoded to: {args.output}")
        else:
            print(decoded, end='')
        
        return 0
        
    except KeyFileError as e:
        print(f"Key error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error decoding: {e}", file=sys.stderr)
        return 1


def cmd_inspect(args) -> int:
    """Execute inspect command."""
    try:
        keyfile = KeyFile.load(args.key)
        
        if args.metadata:
            info = keyfile.get_metadata()
            for key, value in info.items():
                print(f"{key}: {value}")
        else:
            print(keyfile.inspect())
        
        return 0
        
    except KeyFileError as e:
        print(f"Key error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error inspecting key: {e}", file=sys.stderr)
        return 1


def cmd_mix(args) -> int:
    """Execute mix command."""
    try:
        keyfile = KeyFile.load(args.key)

        # At least one mixing method must be requested
        if args.shift is None and not args.reverse and args.seed is None:
            print(
                "Error: No mixing method specified. Use one of: --shift, --reverse, --seed",
                file=sys.stderr
            )
            return 1

        # Let KeyFile.mix validate that only one method is used
        mixed = keyfile.mix(
            shift=args.shift,
            reverse=args.reverse,
            seed=args.seed
        )

        mixed.save(args.output, pretty=args.pretty)

        if not args.quiet:
            print(f"Key remixed: {args.output}")
            print(f"  Source: {mixed.source}")
            print(f"  ASCII range: {mixed.ascii_from}-{mixed.ascii_to}")
            print(f"  Mappings: {len(mixed.encode_map)}")

        return 0

    except KeyFileError as e:
        print(f"Key error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error remixing key: {e}", file=sys.stderr)
        return 1


def cmd_batch(args) -> int:
    """Execute batch encode or decode command."""
    try:
        recursive = args.recursive and not args.no_recursive

        if args.decode:
            # For decode mode, -d/--directory is the source of encoded files,
            # and -o/--output is the destination. If no output is given,
            # decoded files are written into the source directory.
            source_dir = args.directory
            output_dir = args.output or args.directory
            result = decode_batch(
                directory=output_dir,
                key_path=args.key,
                input_path=source_dir,
                mode=args.mode,
                recursive=recursive,
                overwrite=args.overwrite,
                suffix=args.suffix,
                quiet=args.quiet,
                exclude_files=args.exclude_file,
                exclude_dirs=args.exclude_dir,
                exclude_extensions=args.exclude_ext,
                dry_run=args.dry_run,
            )
            action = "decoded"
        else:
            result = encode_batch(
                directory=args.directory,
                key_path=args.key,
                output=args.output,
                mode=args.mode,
                recursive=recursive,
                overwrite=args.overwrite,
                suffix=args.suffix,
                quiet=args.quiet,
                exclude_files=args.exclude_file,
                exclude_dirs=args.exclude_dir,
                exclude_extensions=args.exclude_ext,
                dry_run=args.dry_run,
            )
            action = "encoded"

        if not args.quiet and not result.get("dry_run"):
            print(f"Files {action}:")
            for path in result["files"]:
                print(f"  {path}")

        return 0

    except KeyFileError as e:
        print(f"Key error: {e}", file=sys.stderr)
        return 1
    except BatchEncodingError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        action = "batch decoding" if getattr(args, "decode", False) else "batch encoding"
        print(f"Error {action}: {e}", file=sys.stderr)
        return 1


def main(argv=None) -> int:
    """Main entry point for CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Dispatch to command handler
    commands = {
        "keygen": cmd_keygen,
        "encode": cmd_encode,
        "decode": cmd_decode,
        "inspect": cmd_inspect,
        "mix": cmd_mix,
        "batch": cmd_batch,
    }
    
    handler = commands.get(args.command)
    if handler:
        return handler(args)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
