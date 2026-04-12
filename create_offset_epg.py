import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import copy
import json

with open('offset_config.json', 'r') as f:
    epg_offset_config = json.load(f)
print(epg_offset_config)


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


def create_combined_offset_epg_v2(epg_offset_config, output_file='offset_epg.xml'):
    from collections import defaultdict

    # Group configs by epg_file
    file_to_configs = defaultdict(list)
    for entry in epg_offset_config:
        file_to_configs[entry['epg_file']].append(entry)

    channel_elements = []
    programme_elements = []
    new_root = ET.Element('tv')
    root_attrs_set = False

    for epg_file, configs in file_to_configs.items():
        tree = ET.parse(epg_file)
        root = tree.getroot()

        if not root_attrs_set:
            for attr, val in root.attrib.items():
                new_root.set(attr, val)
            root_attrs_set = True

        config_map = {cfg['channelid']: cfg for cfg in configs}

        for channel in root.findall('channel'):
            ch_id = channel.get('id')
            if ch_id in config_map:
                cfg = config_map[ch_id]
                new_channel = copy.deepcopy(channel)
                new_channel.set('id', cfg['new_channelid'])
                rules = cfg.get('update_displayname', cfg.get('Update displayname', []))
                if rules:
                    apply_displayname_updates(new_channel, rules)
                channel_elements.append(new_channel)

        for programme in root.findall('programme'):
            ch_id = programme.get('channel')
            if ch_id in config_map:
                cfg = config_map[ch_id]
                offset_minutes = int(cfg['offset_minutes'])
                new_prog = copy.deepcopy(programme)

                start_dt, _, tz_str = parse_xmltv_datetime(programme.get('start'))
                new_prog.set('start', format_xmltv_datetime(start_dt + timedelta(minutes=offset_minutes), tz_str))

                stop_dt, _, tz_str_stop = parse_xmltv_datetime(programme.get('stop'))
                new_prog.set('stop', format_xmltv_datetime(stop_dt + timedelta(minutes=offset_minutes), tz_str_stop))

                new_prog.set('channel', cfg['new_channelid'])
                programme_elements.append(new_prog)

    for ch in channel_elements:
        new_root.append(ch)
    for prog in programme_elements:
        new_root.append(prog)

    ET.indent(new_root, space='  ')
    new_tree = ET.ElementTree(new_root)

    with open(output_file, 'wb') as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        new_tree.write(f, encoding='utf-8', xml_declaration=False)

    print(f"Offset EPG written to: {output_file}")
    print(f"Channels: {len(channel_elements)}, Programmes: {len(programme_elements)}")


create_combined_offset_epg_v2(epg_offset_config, output_file='offset_epg.xml')
