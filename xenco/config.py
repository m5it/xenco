"""
xEnco Configuration

User configuration management and defaults.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any


DEFAULT_ASCII_FROM = 32
DEFAULT_ASCII_TO = 127
DEFAULT_CONFIG_DIR = "~/.xenco"
DEFAULT_KEY_DIR = "~/.xenco/keys"


DEFAULT_CONFIG = {
    "ascii_range": {
        "from": DEFAULT_ASCII_FROM,
        "to": DEFAULT_ASCII_TO
    },
    "key_directory": DEFAULT_KEY_DIR,
    "http": {
        "timeout": 30,
        "headers": {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36"
            )
        }
    },
    "output": {
        "format": "text",
        "pretty_print_keys": False,
        "progress_indicator": True,
        "default_chunk_size": 8192
    },
    "auto_save_keys": True,
    "key_file_extension": ".xenco",
    "verify_checksums": True
}


class ConfigError(Exception):
    """Exception raised for configuration errors."""
    pass


class Config:
    """
    Configuration manager for xenco.
    
    Manages user preferences stored in ~/.xenco/config.json.
    Provides defaults and allows customization of:
    - ASCII range for key generation
    - Key storage directory
    - HTTP settings (headers, timeout)
    - Output preferences (format, progress indicators)
    - Auto-save behavior
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to config file (default: ~/.xenco/config.json)
        """
        self._config_dir = Path(DEFAULT_CONFIG_DIR).expanduser()
        self._config_path = Path(config_path) if config_path else self._config_dir / "config.json"
        self._data: Dict[str, Any] = {}
        self._loaded = False
        
        # Load or create default config
        self._ensure_config()
    
    def _ensure_config(self) -> None:
        """Ensure configuration directory and file exist."""
        # Create config directory if needed
        self._config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create default key directory
        key_dir = Path(DEFAULT_KEY_DIR).expanduser()
        key_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing or create default
        if self._config_path.exists():
            self.load()
        else:
            self._data = DEFAULT_CONFIG.copy()
            self.save()
    
    def load(self) -> None:
        """
        Load configuration from file.
        
        Raises:
            ConfigError: If config file is invalid
        """
        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            
            # Merge with defaults to ensure all keys exist
            self._data = self._merge_with_defaults(loaded)
            self._loaded = True
            
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in config file {self._config_path}: {e}")
        except Exception as e:
            raise ConfigError(f"Failed to load config from {self._config_path}: {e}")
    
    def save(self) -> None:
        """
        Save configuration to file.
        
        Raises:
            ConfigError: If config cannot be saved
        """
        try:
            # Ensure directory exists
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2)
                f.write('\n')
                
        except Exception as e:
            raise ConfigError(f"Failed to save config to {self._config_path}: {e}")
    
    def _merge_with_defaults(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge user config with defaults.
        
        Ensures all default keys exist while preserving user settings.
        """
        result = DEFAULT_CONFIG.copy()
        
        for key, value in user_config.items():
            if key in result and isinstance(value, dict) and isinstance(result[key], dict):
                # Deep merge for nested dicts
                result[key].update(value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Supports dot notation for nested keys (e.g., 'ascii_range.from').
        
        Args:
            key: Configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Supports dot notation for nested keys.
        
        Args:
            key: Configuration key
            value: Value to set
        
        Raises:
            ConfigError: If key is invalid
        """
        keys = key.split('.')
        target = self._data
        
        # Navigate to parent
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        # Set value
        target[keys[-1]] = value
    
    @property
    def ascii_from(self) -> int:
        """Get default ASCII range start."""
        return self.get('ascii_range.from', DEFAULT_ASCII_FROM)
    
    @ascii_from.setter
    def ascii_from(self, value: int) -> None:
        """Set default ASCII range start."""
        self.set('ascii_range.from', int(value))
    
    @property
    def ascii_to(self) -> int:
        """Get default ASCII range end."""
        return self.get('ascii_range.to', DEFAULT_ASCII_TO)
    
    @ascii_to.setter
    def ascii_to(self, value: int) -> None:
        """Set default ASCII range end."""
        self.set('ascii_range.to', int(value))
    
    @property
    def key_directory(self) -> Path:
        """Get key storage directory."""
        path = self.get('key_directory', DEFAULT_KEY_DIR)
        return Path(path).expanduser()
    
    @key_directory.setter
    def key_directory(self, path: str) -> None:
        """Set key storage directory."""
        self.set('key_directory', path)
        # Ensure directory exists
        Path(path).expanduser().mkdir(parents=True, exist_ok=True)
    
    @property
    def http_timeout(self) -> int:
        """Get HTTP request timeout."""
        return self.get('http.timeout', 30)
    
    @http_timeout.setter
    def http_timeout(self, seconds: int) -> None:
        """Set HTTP request timeout."""
        self.set('http.timeout', int(seconds))
    
    @property
    def http_headers(self) -> Dict[str, str]:
        """Get HTTP request headers."""
        return self.get('http.headers', DEFAULT_CONFIG['http']['headers'])
    
    @http_headers.setter
    def http_headers(self, headers: Dict[str, str]) -> None:
        """Set HTTP request headers."""
        self.set('http.headers', headers)
    
    @property
    def auto_save_keys(self) -> bool:
        """Get auto-save keys setting."""
        return self.get('auto_save_keys', True)
    
    @auto_save_keys.setter
    def auto_save_keys(self, value: bool) -> None:
        """Set auto-save keys setting."""
        self.set('auto_save_keys', bool(value))
    
    @property
    def pretty_print_keys(self) -> bool:
        """Get pretty print setting for key files."""
        return self.get('output.pretty_print_keys', False)
    
    @pretty_print_keys.setter
    def pretty_print_keys(self, value: bool) -> None:
        """Set pretty print setting for key files."""
        self.set('output.pretty_print_keys', bool(value))
    
    @property
    def progress_indicator(self) -> bool:
        """Get progress indicator setting."""
        return self.get('output.progress_indicator', True)
    
    @progress_indicator.setter
    def progress_indicator(self, value: bool) -> None:
        """Set progress indicator setting."""
        self.set('output.progress_indicator', bool(value))
    
    def get_key_path(self, name: str) -> Path:
        """
        Get full path for a key file.
        
        Args:
            name: Key file name (with or without extension)
        
        Returns:
            Full path to key file
        """
        key_dir = self.key_directory
        
        # Add extension if missing
        ext = self.get('key_file_extension', '.xenco')
        if not name.endswith(ext):
            name = name + ext
        
        return key_dir / name
    
    def list_keys(self) -> list:
        """
        List all key files in key directory.
        
        Returns:
            List of key file names
        """
        key_dir = self.key_directory
        
        if not key_dir.exists():
            return []
        
        ext = self.get('key_file_extension', '.xenco')
        return [f.name for f in key_dir.glob(f'*{ext}') if f.is_file()]
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self._data = DEFAULT_CONFIG.copy()
        self.save()
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self._data.copy()
    
    def __repr__(self) -> str:
        return f"Config({self._config_path})"
