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
    }
    
    handler = commands.get(args.command)
    if handler:
        return handler(args)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
