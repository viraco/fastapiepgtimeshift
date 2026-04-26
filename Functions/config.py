import os

from dotenv import load_dotenv
import json


class Config():
    """Configuration manager with refreshable EPG configs"""

    def __init__(self, base_dir=None, config_dir=None, data_dir=None):
        """Initialize configuration with directory paths"""
        if base_dir is None:
            base_dir = os.path.dirname(__file__)

        self.base_dir = base_dir
        self.config_dir = config_dir if config_dir else os.path.join(base_dir, '..', 'Config')
        self.data_dir = data_dir if data_dir else os.path.join(base_dir, '..', 'Data')

        self._epg_offset_config = None
        self._epg_combine_config = None

        self.load_env_config()
        self.refresh_epg_configs()

    def load_env_config(self):
        """Load configuration from config.env file"""
        config_path = os.path.join(self.base_dir, '..', 'Config', 'config.env')
        load_dotenv(config_path, override=True)

    def _load_epg_offset_config(self):
        """Load EPG offset configuration from JSON file"""
        file_name = 'offset_config.json'
        config_file = os.path.join(self.config_dir, file_name)
        with open(config_file, 'r') as f:
            return json.load(f)

    def _load_epg_combine_config(self):
        """Load EPG combine configuration from JSON file"""
        file_name = 'combine_epg.json'
        config_file = os.path.join(self.config_dir, file_name)
        with open(config_file, 'r') as f:
            return json.load(f)

    def refresh_epg_configs(self):
        """Refresh both EPG offset and combine configurations"""
        self._epg_offset_config = self._load_epg_offset_config()
        self._epg_combine_config = self._load_epg_combine_config()

    @property
    def epg_offset_config(self):
        """Get EPG offset configuration"""
        return self._epg_offset_config

    @property
    def epg_combine_config(self):
        """Get EPG combine configuration"""
        return self._epg_combine_config


#def load_config():
#    """Load configuration from config.env file (backward compatibility)"""
#    Config.load_env_config()


#def get_epg_offset_config(base_dir=None):
#    """Get EPG offset configuration (backward compatibility)"""
#    if base_dir is None:
#        base_dir = os.path.join(os.path.dirname(__file__), '..', 'Config')
#    file_name = 'offset_config.json'
#    config_file = os.path.join(base_dir, file_name)
#    with open(config_file, 'r') as f:
#        epg_offset_config = json.load(f)
#    return epg_offset_config


#def get_epg_combine_config(base_dir=None):
#    """Get EPG combine configuration (backward compatibility)"""
#    file_name = 'combine_epg.json'
#    if base_dir is None:
#        base_dir = os.path.join(os.path.dirname(__file__), '..', 'Config')
#    config_file = os.path.join(base_dir, file_name)
#    with open(config_file, 'r') as f:
#        epg_combine_config = json.load(f)
#    return epg_combine_config