"""
Configuration loader with variable substitution support.

Supports ${VAR} patterns in YAML config files for:
- ${SERVER_ROOT} - path to the current server directory
- ${PROJECT_ROOT} - path to the project root
- Any environment variable

Variables are substituted recursively throughout the config dictionary.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


def _substitute_variables(
    value: Any, server_root: Optional[Path] = None, project_root: Optional[Path] = None
) -> Any:
    """
    Recursively substitute ${VAR} patterns in config values.

    Args:
        value: The config value to process (can be str, dict, list, or other)
        server_root: Path to the server root directory
        project_root: Path to the project root directory

    Returns:
        The value with all ${VAR} patterns substituted
    """
    if isinstance(value, str):
        # Replace ${VAR} patterns with environment variables or defaults
        def replacer(match: re.Match) -> str:
            var_name = match.group(1)

            # Handle special variables
            if var_name == "SERVER_ROOT":
                if server_root is None:
                    raise ValueError(
                        "${SERVER_ROOT} used in config but server_root not provided"
                    )
                return str(server_root)
            elif var_name == "PROJECT_ROOT":
                if project_root is None:
                    raise ValueError(
                        "${PROJECT_ROOT} used in config but project_root not provided"
                    )
                return str(project_root)

            # Try environment variable
            if var_name in os.environ:
                return os.environ[var_name]

            raise ValueError(
                f"Variable ${{{var_name}}} not found in environment "
                "and not a special variable (SERVER_ROOT, PROJECT_ROOT)"
            )

        # Replace all ${VAR} patterns
        return re.sub(r"\$\{([^}]+)\}", replacer, value)

    elif isinstance(value, dict):
        # Recursively process dictionary values
        return {
            key: _substitute_variables(val, server_root, project_root)
            for key, val in value.items()
        }

    elif isinstance(value, list):
        # Recursively process list items
        return [_substitute_variables(item, server_root, project_root) for item in value]

    else:
        # Return other types as-is
        return value


def load_config_with_substitution(
    config_path: str, server_root: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Load YAML config file with variable substitution support.

    Args:
        config_path: Path to YAML config file (can be relative or absolute)
        server_root: Path to the server root directory. If None, uses parent of config file.

    Returns:
        Dictionary with all ${VAR} patterns substituted

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If variable substitution fails
        yaml.YAMLError: If YAML parsing fails
    """
    config_file = Path(config_path)

    # Try to resolve relative paths
    if not config_file.is_absolute():
        # First try relative to current working directory
        if Path(config_file).exists():
            config_file = config_file.resolve()
        else:
            # Try relative to project root (two levels up from shared/preprocessing/src)
            project_root = Path(__file__).parent.parent.parent.parent
            alternative = project_root / config_file
            if alternative.exists():
                config_file = alternative
            else:
                raise FileNotFoundError(
                    f"Config file not found: {config_path}\n"
                    f"  Tried: {config_file.resolve()}\n"
                    f"  Tried: {alternative}"
                )

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    # Determine project root if not provided
    if server_root is None:
        # If config is in servers/{name}/config/, use servers/{name} as server_root
        parts = config_file.parts
        if "servers" in parts and "config" in parts:
            servers_idx = parts.index("servers")
            config_idx = parts.index("config")
            if config_idx > servers_idx + 1:
                server_root = Path(*parts[: config_idx - 1])

    # Determine project root (parent of .git or shared/)
    project_root = config_file
    while project_root != project_root.parent:
        project_root = project_root.parent
        if (project_root / ".git").exists() or (project_root / "shared").exists():
            break

    # Load YAML file
    with open(config_file, "r") as f:
        config = yaml.safe_load(f) or {}

    # Perform variable substitution
    config = _substitute_variables(config, server_root, project_root)

    return config
