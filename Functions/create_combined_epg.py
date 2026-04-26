import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import copy
import os
import logging
from collections import defaultdict
from Functions.config import Config

logger = logging.getLogger(__name__)


def parse_xmltv_datetime(dt_str):
    """Parse XMLTV datetime format: YYYYMMDDHHMMSS +HHMM"""
    dt_str = dt_str.strip()
    parts = dt_str.split(' ')
    dt = datetime.strptime(parts[0], '%Y%m%d%H%M%S')
    offset_str = parts[1] if len(parts) > 1 else '+0000'
    sign = 1 if offset_str[0] == '+' else -1
    offset_hours = int(offset_str[1:3])
    offset_mins = int(offset_str[3:5])
    tz_offset = timedelta(hours=offset_hours, minutes=offset_mins) * sign
    return dt, tz_offset, offset_str


def format_xmltv_datetime(dt, tz_str):
    """Format datetime back to XMLTV format"""
    return dt.strftime('%Y%m%d%H%M%S') + ' ' + tz_str


def apply_displayname_updates(element, update_displayname_rules):
    """Apply find/replace rules to all <display-name> child elements."""
    for display_name in element.findall('display-name'):
        if display_name.text:
            for rule in update_displayname_rules:
                display_name.text = display_name.text.replace(rule['find'], rule['replace'])


def create_combined_epg(epg_combine_config, data_dir=None):
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'Data')

    # Group configs by epg_file
    file_to_configs = defaultdict(list)
    for entry in epg_combine_config:
        file_path = os.path.normpath(os.path.join(data_dir, entry['epg_file']))
        file_to_configs[file_path].append(entry)

    channel_elements = []
    programme_elements = []
    new_root = ET.Element('tv')
    root_attrs_set = False

    for epg_file, configs in file_to_configs.items():
        logger.info(f"Processing EPG file: {epg_file}")
        tree = ET.parse(epg_file, ET.XMLParser(encoding='utf-8'))
        root = tree.getroot()

        if not root_attrs_set:
            for attr, val in root.attrib.items():
                new_root.set(attr, val)
            root_attrs_set = True

        config_map = {}
        for cfg in configs:
            for ch_cfg in cfg.get('channels', []):
                config_map[ch_cfg['channelid']] = {'parent_cfg': cfg, 'channel_cfg': ch_cfg}

        for channel in root.findall('channel'):
            ch_id = channel.get('id')
            if ch_id in config_map:
                ch_cfg = config_map[ch_id]['channel_cfg']
                new_channel = copy.deepcopy(channel)
                rules = ch_cfg.get('update_displayname', [])
                if rules:
                    apply_displayname_updates(new_channel, rules)
                channel_elements.append(new_channel)

        for programme in root.findall('programme'):
            ch_id = programme.get('channel')
            if ch_id in config_map:
                new_prog = copy.deepcopy(programme)
                programme_elements.append(new_prog)

    for ch in channel_elements:
        new_root.append(ch)
    for prog in programme_elements:
        new_root.append(prog)

    ET.indent(new_root, space='  ')
    new_tree = ET.ElementTree(new_root)

    output_file = os.path.join(data_dir, 'combined_epg.xml')

    with open(output_file, 'wb') as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        new_tree.write(f, encoding='utf-8', xml_declaration=False)

    logger.info(f"Combined EPG written to: {output_file}")
    logger.info(f"Channels: {len(channel_elements)}, Programmes: {len(programme_elements)}")


if __name__ == "__main__":
    from Functions.logging_config import setup_logging
    setup_logging()
    _default_config = Config()
    _default_config.base_dir = os.path.dirname(__file__)
    _default_config.config_dir = os.path.join(os.path.dirname(__file__), 'Config')
    _default_config.data_dir = os.path.join(os.path.dirname(__file__), 'Data')
    base_dir = _default_config.base_dir
    config_dir = _default_config.config_dir
    data_dir = _default_config.data_dir

    _default_config.load_env_config()
    _default_config.refresh_epg_configs()

    create_combined_epg(_default_config._load_epg_combine_config(), data_dir=None)
