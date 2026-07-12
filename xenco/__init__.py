"""
xEnco - Text Encoder/Decoder with Dynamic Key Generation

A Python package for encoding/decoding text using dynamically generated
keys from any data source (URLs, files, or text).

Version: 1.1.0
Author: madK0s
"""

__version__ = "1.1.0"
__author__ = "madK0s"

from .encoder import Encoder
from .keygen import KeyGenerator, generate_key
from .keyfile import KeyFile

__all__ = ["Encoder", "KeyGenerator", "KeyFile", "generate_key"]
