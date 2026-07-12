"""
Tests for xenco.cli module.
"""

import pytest
from xenco.cli import create_parser


class TestCLIParser:
    """Test CLI argument parsing."""
    
    def test_create_parser(self):
        """Test parser creation."""
        parser = create_parser()
        assert parser is not None
    
    def test_version_flag(self, capsys):
        """Test --version flag."""
        parser = create_parser()
        
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])
        
        assert exc_info.value.code == 0
    
    def test_no_command_shows_help(self, capsys):
        """Test no command shows help."""
        parser = create_parser()
        
        # Should not raise, just print help
        args = parser.parse_args([])
        assert args.command is None
    
    def test_encode_requires_key(self):
        """Test encode requires --key."""
        parser = create_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args(["encode"])
    
    def test_encode_with_key(self):
        """Test encode with required args."""
        parser = create_parser()
        args = parser.parse_args(["encode", "-k", "test.xenco", "-i", "input.txt"])
        
        assert args.command == "encode"
        assert args.key == "test.xenco"
        assert args.input == "input.txt"
        assert args.output == "-"  # Default
    
    def test_decode_with_key(self):
        """Test decode with required args."""
        parser = create_parser()
        args = parser.parse_args(["decode", "-k", "test.xenco", "-i", "encoded.txt"])
        
        assert args.command == "decode"
        assert args.key == "test.xenco"
    
    def test_keygen_requires_source_and_output(self):
        """Test keygen requires --source and --output."""
        parser = create_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args(["keygen", "-s", "source.txt"])
    
    def test_keygen_with_args(self):
        """Test keygen with all args."""
        parser = create_parser()
        args = parser.parse_args([
            "keygen",
            "-s", "https://example.com",
            "-o", "output.xenco",
            "-f", "40",
            "-t", "120",
            "--pretty"
        ])
        
        assert args.command == "keygen"
        assert args.source == "https://example.com"
        assert args.output == "output.xenco"
        assert args.ascii_from == 40
        assert args.ascii_to == 120
        assert args.pretty is True
    
    def test_inspect_requires_key(self):
        """Test inspect requires --key."""
        parser = create_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args(["inspect"])
    
    def test_inspect_with_key(self):
        """Test inspect with key."""
        parser = create_parser()
        args = parser.parse_args(["inspect", "-k", "test.xenco"])
        
        assert args.command == "inspect"
        assert args.key == "test.xenco"
        assert args.metadata is False
    
    def test_inspect_metadata(self):
        """Test inspect --metadata."""
        parser = create_parser()
        args = parser.parse_args(["inspect", "-k", "test.xenco", "--metadata"])
        
        assert args.metadata is True
    
    def test_verbose_flag(self):
        """Test --verbose flag."""
        parser = create_parser()
        args = parser.parse_args(["--verbose", "encode", "-k", "test.xenco"])
        
        assert args.verbose is True
    
    def test_quiet_flag(self):
        """Test --quiet flag."""
        parser = create_parser()
        args = parser.parse_args(["--quiet", "encode", "-k", "test.xenco"])
        
        assert args.quiet is True
