from .defaults import DEFAULTS
from .env import load_env_values
from .validators import validate_config

def load_config(overrides=None):
    config = DEFAULTS.copy()

    # Merge environment variables
    config.update(load_env_values())

    # Merge explicit overrides (used in tests)
    if overrides:
        config.update(overrides)

    return validate_config(config)