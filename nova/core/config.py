"""
Professional Configuration Management for NOVA

Handles environment variables, settings validation, and configuration loading
with professional error handling and type safety.
"""

import os
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from dotenv import load_dotenv


@dataclass
class NovaConfig:
    """Professional configuration class for NOVA."""
    
    # Core Settings
    name: str = "NOVA"
    version: str = "2.0.0"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    
    # Data Directories
    data_dir: Path = field(default_factory=lambda: Path("./data"))
    cache_dir: Path = field(default_factory=lambda: Path("./cache"))
    logs_dir: Path = field(default_factory=lambda: Path("./logs"))
    
    # API Configuration
    api_host: str = "localhost"
    api_port: int = 8000
    
    # AI Model Configuration
    default_ai_model: str = "fallback"
    gemini_model: str = "gemini-1.5-pro"
    openai_model: str = "gpt-3.5-turbo"
    anthropic_model: str = "claude-3-sonnet-20240229"
    fallback_model: str = "local"
    
    # API Keys (will be loaded from environment)
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # AI Settings
    ai_temperature: float = 0.7
    ai_max_tokens: int = 2048
    ai_timeout: int = 30
    ai_retry_attempts: int = 3
    
    # Feature Flags
    enable_voice: bool = False
    enable_vision: bool = False
    enable_web_search: bool = False
    enable_file_operations: bool = True
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "NovaConfig":
        """Load configuration from environment file."""
        if config_path:
            load_dotenv(config_path)
        else:
            # Try multiple common config file locations
            config_files = [".env", ".env.local", "config/.env"]
            for config_file in config_files:
                if Path(config_file).exists():
                    load_dotenv(config_file)
                    break
        
        return cls(
            name=os.getenv("NOVA_NAME", "NOVA"),
            environment=os.getenv("NOVA_ENV", "development"),
            debug=os.getenv("NOVA_DEBUG", "false").lower() == "true",
            log_level=os.getenv("NOVA_LOG_LEVEL", "INFO"),
            
            # Directories
            data_dir=Path(os.getenv("NOVA_DATA_DIR", "./data")),
            cache_dir=Path(os.getenv("NOVA_CACHE_DIR", "./cache")),
            logs_dir=Path(os.getenv("NOVA_LOGS_DIR", "./logs")),
            
            # API
            api_host=os.getenv("API_HOST", "localhost"),
            api_port=int(os.getenv("API_PORT", "8000")),
            
            # AI Models
            default_ai_model=os.getenv("DEFAULT_AI_MODEL", "fallback"),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-pro"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
            fallback_model=os.getenv("FALLBACK_MODEL", "local"),
            
            # API Keys
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            
            # AI Settings
            ai_temperature=float(os.getenv("AI_TEMPERATURE", "0.7")),
            ai_max_tokens=int(os.getenv("AI_MAX_TOKENS", "2048")),
            ai_timeout=int(os.getenv("AI_TIMEOUT", "30")),
            ai_retry_attempts=int(os.getenv("AI_RETRY_ATTEMPTS", "3")),
            
            # Features
            enable_voice=os.getenv("ENABLE_VOICE", "false").lower() == "true",
            enable_vision=os.getenv("ENABLE_VISION", "false").lower() == "true",
            enable_web_search=os.getenv("ENABLE_WEB_SEARCH", "false").lower() == "true",
            enable_file_operations=os.getenv("ENABLE_FILE_OPERATIONS", "true").lower() == "true",
        )
    
    def create_directories(self):
        """Create necessary directories if they don't exist."""
        for directory in [self.data_dir, self.cache_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> Dict[str, Any]:
        """Validate configuration and return validation results."""
        issues = []
        warnings = []
        
        # Check if at least one AI API key is configured
        api_keys = [self.gemini_api_key, self.openai_api_key, self.anthropic_api_key]
        if not any(api_keys):
            warnings.append("No AI API keys configured - only local fallback responses will be available")
        
        # Validate directories are writable
        for name, directory in [
            ("data", self.data_dir),
            ("cache", self.cache_dir),
            ("logs", self.logs_dir)
        ]:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                # Test write access
                test_file = directory / ".write_test"
                test_file.touch()
                test_file.unlink()
            except Exception as e:
                issues.append(f"Cannot write to {name} directory ({directory}): {e}")
        
        # Validate AI settings
        if not 0.0 <= self.ai_temperature <= 2.0:
            issues.append(f"AI temperature must be between 0.0 and 2.0, got {self.ai_temperature}")
        
        if self.ai_max_tokens < 1:
            issues.append(f"AI max tokens must be positive, got {self.ai_max_tokens}")
        
        if self.ai_timeout < 1:
            issues.append(f"AI timeout must be positive, got {self.ai_timeout}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def __post_init__(self):
        """Post-initialization validation and setup."""
        # Convert string paths to Path objects if needed
        if isinstance(self.data_dir, str):
            self.data_dir = Path(self.data_dir)
        if isinstance(self.cache_dir, str):
            self.cache_dir = Path(self.cache_dir)
        if isinstance(self.logs_dir, str):
            self.logs_dir = Path(self.logs_dir)
        
        # Create directories
        self.create_directories()
        
        # Validate configuration
        validation = self.validate()
        if not validation["valid"]:
            logger = logging.getLogger(__name__)
            for issue in validation["issues"]:
                logger.error(f"Configuration error: {issue}")
            raise ValueError(f"Invalid configuration: {', '.join(validation['issues'])}")
        
        if validation["warnings"]:
            logger = logging.getLogger(__name__)
            for warning in validation["warnings"]:
                logger.warning(f"Configuration warning: {warning}")
