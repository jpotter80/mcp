#!/usr/bin/env python3
"""Test config loader variable substitution."""

import json
from shared.config_loader import load_config_with_substitution

config = load_config_with_substitution('servers/mojo-manual-mcp/config/processing_config.yaml')
print('Source:', config['source']['directory'])
print('Output:', config['output']['base_directory'])
print('\nFull config:')
print(json.dumps(config, indent=2))
