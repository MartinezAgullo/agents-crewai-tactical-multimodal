import yaml
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


def load_execution_config() -> Dict[str, Any]:
    """
    Load execution configuration from YAML.
    
    Returns:
        Dictionary containing execution and logging configuration
    """
    # Determine config path relative to this file
    config_path = Path(__file__).parent / "execution_config.yaml"
    
    # Default configuration
    defaults = {
        'execution': {
            'execute_LLM_manager': True,
            'enable_MQTT_consumer': False,
            'enable_telemetry': False
        },
        'logging': {
            'level': 'INFO',
            'show_llm_status': True,
            'show_tool_usage': True
        }
    }
    
    if not config_path.exists():
        logger.warning(
            f"Execution config not found at {config_path}\n"
            f"Using default configuration"
        )
        return defaults
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate structure
        if not config or 'execution' not in config:
            logger.warning("Invalid config structure, using defaults")
            return defaults
        
        logger.info(f"✅ Loaded execution config from {config_path}")
        return config
        
    except yaml.YAMLError as e:
        logger.error(f"❌ YAML parsing error: {e}")
        logger.warning("Using default configuration")
        return defaults
    except Exception as e:
        logger.error(f"❌ Error loading config: {e}")
        logger.warning("Using default configuration")
        return defaults