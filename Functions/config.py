import os

from dotenv import load_dotenv
import json


def load_config():
    """Load configuration from config.env file"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'Config', 'config.env')
    load_dotenv(config_path, override=True)


def get_epg_offset_config(base_dir=None):
    file_name = 'offset_config.json'
    if base_dir is None:
        base_dir = os.path.join(os.path.dirname(__file__), '..', 'Config')
    config_file = os.path.join(base_dir, file_name)
    with open(config_file, 'r') as f:
        epg_offset_config = json.load(f)
    return epg_offset_config


def get_epg_combine_config(base_dir=None):
    file_name = 'combine_epg.json'
    if base_dir is None:
        base_dir = os.path.join(os.path.dirname(__file__), '..', 'Config')
    config_file = os.path.join(base_dir, file_name)
    with open(config_file, 'r') as f:
        epg_offset_config = json.load(f)
    return epg_offset_config
