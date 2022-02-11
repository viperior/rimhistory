"""Extract data from a RimWorld save file"""

import json
import logging
import os


def get_save_file_path() -> str:
    """Return the path to the RimWorld save file to analyze as a string

    Parameters:
    None

    Returns:
    str: The path to the save game file as configured in config.json
    """
    with open("config.json", "r", encoding="utf_8") as config_file:
        config_data = json.load(config_file)

    rimworld_save_file_path = config_data["rimworld_save_file_path"]
    logging.debug("Retrieved location of save game from config file: %s", rimworld_save_file_path)

    return rimworld_save_file_path


def get_save_file_size() -> int:
    """Return the file size of the RimWorld save

    Parameters:
    None

    Returns:
    int: The file size as reported by os.stat()
    """
    rimworld_save_file_path = get_save_file_path()
    file_size = os.path.getsize(rimworld_save_file_path)

    return file_size
