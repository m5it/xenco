#!/usr/bin/env python3
"""
xEnco standalone launcher.

Run the xenco CLI without installing the package::

    python main.py keygen -s "https://example.com" -o key.xenco
    echo "Hello, World!" | python main.py encode -k key.xenco
    python main.py decode -i encoded.txt -k key.xenco -o decoded.txt
    python main.py inspect -k key.xenco
    python main.py --help
"""

import sys
from pathlib import Path

# Ensure the local xenco package is importable when running without install.
_PROJECT_ROOT = Path(__file__).resolve().parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from xenco.cli import main


if __name__ == "__main__":
    sys.exit(main())
