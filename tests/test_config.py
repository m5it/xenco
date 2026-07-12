"""
Tests for xenco.config module.
"""

import pytest
import json
from xenco.config import Config, ConfigError, DEFAULT_CONFIG


class TestConfig:
    """Test Config class."""
    
    def test_init_creates_default(self, temp_dir):
        """Test initialization creates default config."""
        config_path = temp_dir / "config.json"
        config = Config(str(config_path))
        
        assert config_path.exists()
        assert config.get("ascii_range.from") == 32
        assert config.get("ascii_range.to") == 128
    
    def test_load_existing(self, temp_dir):
        """Test loading existing config."""
        config_path = temp_dir / "config.json"
        
        # Create config file
        custom_config = {"ascii_range": {"from": 40, "to": 100}}
        config_path.write_text(json.dumps(custom_config))
        
        config = Config(str(config_path))
        assert config.ascii_from == 40
        assert config.ascii_to == 100
    
    def test_save_and_reload(self, temp_dir):
        """Test saving and reloading config."""
        config_path = temp_dir / "config.json"
        config = Config(str(config_path))
        
        # Modify and save
        config.set("test_key", "test_value")
        config.save()
        
        # Reload
        config2 = Config(str(config_path))
        assert config2.get("test_key") == "test_value"
    
    def test_ascii_from_property(self, temp_dir):
        """Test ascii_from property."""
        config_path = temp_dir / "config.json"
        config = Config(str(config_path))
        
        config.ascii_from = 50
        assert config.ascii_from == 50
    
    def test_ascii_to_property(self, temp_dir):
        """Test ascii_to property."""
        config_path = temp_dir / "config.json"
        config = Config(str(config_path))
        
        config.ascii_to = 120
        assert config.ascii_to == 120
    
    def test_key_directory_property(self, temp_dir):
        """Test key_directory property."""
        config_path = temp_dir / "config.json"
        config = Config(str(config_path))
        
        key_dir = temp_dir / "custom_keys"
        config.key_directory = str(key_dir)
        
        assert config.key_directory == key_dir
        assert key_dir.exists()
    
    def test_http_timeout_property(self, temp_dir):
        """Test http_timeout property."""
        config_path = temp_dir / "config.json"
        config = Config(str(config_path))
        
        config.http_timeout = 60
        assert config.http_timeout == 60
    
    def test_auto_save_keys_property(self, temp_dir):
        """Test auto_save_keys property."""
        config_path = temp_dir / "config.json"
        config = Config(str(config_path))
        
        config.auto_save_keys = False
        assert config.auto_save_keys is False
    
    def test_pretty_print_keys_property(self, temp_dir):
        """Test pretty_print_keys property."""
        config_path = temp_dir / "config.json"
        config = Config(str(config_path))
        
        config.pretty_print_keys = True
        assert config.pretty_print_keys is True
    
    def test_get_key_path(self, temp_dir):
        """Test get_key_path method."""
        config_path = temp_dir / "config.json"
        config = Config(str(config_path))
        
        key_path = config.get_key_path("mykey")
        assert key_path.name == "mykey.xenco"
    
    def test_list_keys(self, temp_dir):
        """Test list_keys method."""
        config_path = temp_dir / "config.json"
        config = Config(str(config_path))
        
        # Create some key files
        key_dir = config.key_directory
        key_dir.mkdir(parents=True, exist_ok=True)
        (key_dir / "key1.xenco").write_text("{}")
        (key_dir / "key2.xenco").write_text("{}")
        
        keys = config.list_keys()
        assert len(keys) == 2
        assert "key1.xenco" in keys
        assert "key2.xenco" in keys
    
    def test_reset_to_defaults(self, temp_dir):
        """Test reset_to_defaults method."""
        config_path = temp_dir / "config.json"
        config = Config(str(config_path))
        
        # Modify
        config.set("custom", "value")
        
        # Reset
        config.reset_to_defaults()
        
        assert config.get("custom") is None
        assert config.ascii_from == DEFAULT_CONFIG["ascii_range"]["from"]
    
    def test_to_dict(self, temp_dir):
        """Test to_dict method."""
        config_path = temp_dir / "config.json"
        config = Config(str(config_path))
        
        data = config.to_dict()
        assert "ascii_range" in data
        assert "key_directory" in data


class TestConfigError:
    """Test ConfigError exception."""
    
    def test_config_error(self):
        """Test ConfigError exception."""
        err = ConfigError("test error")
        assert "test error" in str(err)
    
    def test_invalid_json(self, temp_dir):
        """Test loading invalid JSON raises ConfigError."""
        config_path = temp_dir / "config.json"
        config_path.write_text("not valid json")
        
        with pytest.raises(ConfigError):
            Config(str(config_path))
