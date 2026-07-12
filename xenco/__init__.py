"""
xEnco - Text Encoder/Decoder with Dynamic Key Generation

A Python package for encoding/decoding text using dynamically generated
keys from any data source (URLs, files, or text).

Version: 1.0.0
Author: madK0s (refactored)
"""

__version__ = "1.0.0"
__author__ = "madK0s"

from .encoder import Encoder
from .keygen import KeyGenerator
from .keyfile import KeyFile

__all__ = ["Encoder", "KeyGenerator", "KeyFile"]
