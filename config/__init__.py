"""
Vibe_Alerts - Configuration Management
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def load_config() -> Dict[str, Any]:
    """Load configuration from YAML and environment variables"""
    
    # Get config file path
    config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
    
    # Load YAML config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Add environment variables
    config['database_url'] = os.getenv('DATABASE_URL')
    config['redis_url'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    config['telegram'] = {
        'bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
        'channel_id': os.getenv('TELEGRAM_CHANNEL_ID'),
    }
    
    config['security'] = {
        'jwt_secret': os.getenv('JWT_SECRET_KEY'),
        'admin_password': os.getenv('ADMIN_PASSWORD'),
    }
    
    config['app'] = {
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'debug': os.getenv('DEBUG', 'false').lower() == 'true',
    }
    
    # Override poll_interval if set in env
    if os.getenv('POLL_INTERVAL'):
        config['monitoring']['poll_interval'] = int(os.getenv('POLL_INTERVAL'))
    
    return config


def get_database_url() -> str:
    """Get database URL from environment"""
    url = os.getenv('DATABASE_URL')
    if not url:
        raise ValueError("DATABASE_URL not set in environment")
    return url


def get_redis_url() -> str:
    """Get Redis URL from environment"""
    return os.getenv('REDIS_URL', 'redis://localhost:6379/0')

