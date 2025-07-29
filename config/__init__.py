# Configuration Management for NOVA
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

class ConfigManager:
    """Manages NOVA configuration from files and environment variables"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = Path(config_path)
        self.config_data: Dict[str, Any] = {}
        self.logger = logging.getLogger("nova.config")
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file and environment"""
        # Load from YAML file
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    self.config_data = yaml.safe_load(f) or {}
                self.logger.info(f"Loaded configuration from {self.config_path}")
            except Exception as e:
                self.logger.warning(f"Failed to load config file: {e}")
                self.config_data = {}
        else:
            self.logger.warning(f"Config file not found: {self.config_path}")
            self.config_data = {}
        
        # Override with environment variables
        self._load_env_overrides()
        
        # Ensure required defaults
        self._set_defaults()
    
    def _load_env_overrides(self):
        """Load environment variable overrides"""
        env_mappings = {
            'NOVA_ENV': ['environment'],
            'NOVA_LOG_LEVEL': ['logging', 'level'],
            'NOVA_DATA_DIR': ['storage', 'data_dir'],
            'NOVA_CACHE_DIR': ['storage', 'cache_dir'],
            'API_HOST': ['api', 'host'],
            'API_PORT': ['api', 'port'],
            'OPENAI_API_KEY': ['apis', 'openai_key'],
            'ANTHROPIC_API_KEY': ['apis', 'anthropic_key'],
            'SECURITY_MONITORING': ['security', 'real_time_monitoring'],
            'SECURITY_AUTO_RESPONSE': ['security', 'auto_threat_response']
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested_config(config_path, value)
    
    def _set_nested_config(self, path: list, value: str):
        """Set nested configuration value"""
        current = self.config_data
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Convert string values to appropriate types
        if value.lower() in ['true', 'false']:
            value = value.lower() == 'true'
        elif value.isdigit():
            value = int(value)
        
        current[path[-1]] = value
    
    def _set_defaults(self):
        """Set default configuration values"""
        defaults = {
            'nova': {
                'name': 'NOVA',
                'version': '0.1.0',
                'personality': 'assistant',
                'debug_mode': False
            },
            'api': {
                'host': 'localhost',
                'port': 8000,
                'cors_enabled': True,
                'docs_enabled': True
            },
            'storage': {
                'data_dir': './data',
                'cache_dir': './cache',
                'logs_dir': './logs',
                'backup_dir': './backups'
            },
            'security': {
                'real_time_monitoring': True,
                'auto_threat_response': True,
                'data_encryption': True,
                'security_level': 'high'
            },
            'capabilities': {
                'voice_enabled': True,
                'vision_enabled': True,
                'security_enabled': True,
                'learning_enabled': True
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file_enabled': True,
                'console_enabled': True
            },
            'agents': {
                'max_concurrent': 5,
                'timeout_seconds': 300,
                'retry_attempts': 3
            }
        }
        
        # Merge defaults with existing config
        self._deep_merge(defaults, self.config_data)
        self.config_data = defaults
    
    def _deep_merge(self, defaults: dict, config: dict):
        """Deep merge configuration dictionaries"""
        for key, value in config.items():
            if key in defaults and isinstance(defaults[key], dict) and isinstance(value, dict):
                self._deep_merge(defaults[key], value)
            else:
                defaults[key] = value
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated path"""
        keys = path.split('.')
        current = self.config_data
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def set(self, path: str, value: Any):
        """Set configuration value by dot-separated path"""
        keys = path.split('.')
        current = self.config_data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def save(self, path: Optional[str] = None):
        """Save configuration to file"""
        save_path = Path(path) if path else self.config_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(save_path, 'w') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, indent=2)
            self.logger.info(f"Configuration saved to {save_path}")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def reload(self):
        """Reload configuration from file"""
        self._load_config()
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary"""
        return self.config_data.copy()
    
    def create_dirs(self):
        """Create necessary directories from configuration"""
        dirs_to_create = [
            self.get('storage.data_dir'),
            self.get('storage.cache_dir'),
            self.get('storage.logs_dir'),
            self.get('storage.backup_dir'),
            f"{self.get('storage.data_dir')}/chroma_db"
        ]
        
        for dir_path in dirs_to_create:
            if dir_path:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Created directory: {dir_path}")

# Global configuration instance
config = ConfigManager()
