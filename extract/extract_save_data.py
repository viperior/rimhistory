"""Extract data from a RimWorld save file"""

import json
import logging
import os
import xml.etree.ElementTree


def extract_game_version() -> str:
    """Return the base RimWorld game version from the save file's meta element"""
    root = get_save_file_data(save_file_path=get_save_file_path())

    return root.find("./meta/gameVersion").text


def extract_mod_list() -> list:
    """Extract the list of mods installed in the save game

    Parameters:
    None

    Returns:
    list: A list of dictionaries with each installed mod's metadata
    """
    root = get_save_file_data(save_file_path=get_save_file_path())
    mod_ids = root.findall("./meta/modIds")
    mod_steam_ids = root.findall("./meta/modSteamIds")
    mod_names = root.findall("./meta/modNames")
    mod_list = []

    for index, mod_id in enumerate(mod_ids[0]):
        mod_info = {
            "mod_id": mod_id.text,
            "mod_name": mod_names[0][index].text,
            "mod_steam_id": mod_steam_ids[0][index].text
        }
        mod_list.append(mod_info)

    return mod_list


def extract_rimworld_save_data() -> None:
    """Recurse through all the data

    Parameters:
    None

    Returns:
    None
    """
    save_file_path = get_save_file_path()
    logging.debug("Processing save file: %s", save_file_path)
    root = get_save_file_data(save_file_path=save_file_path)
    logging.debug("Starting recursion")
    recurse_children(root)
    logging.debug("Recursion complete")


def get_save_file_data(save_file_path) -> xml.etree.ElementTree.Element:
    """Return the root object from the RimWorld save game XML data"""
    tree = xml.etree.ElementTree.parse(save_file_path)
    root = tree.getroot()

    return root


def get_save_file_path() -> str:
    """Return the path to the RimWorld save file to analyze as a string"""
    with open("config.json", "r", encoding="utf_8") as config_file:
        config_data = json.load(config_file)

    rimworld_save_file_path = config_data["rimworld_save_file_path"]
    print(rimworld_save_file_path)

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


def recurse_children(parent) -> None:
    """Recurse through all the children of an element

    Parameters:
    None

    Returns:
    None
    """
    logging.debug("tag: %s; attributes: %s; text: %s", parent.tag, parent.attrib, parent.text)

    for index, child in enumerate(parent):
        recurse_children(child)

        if index >= 10:
            logging.debug("10 siblings belong to parent element have been scanned. Skipping to next\
                 parent node")
            break
