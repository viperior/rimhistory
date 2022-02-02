"""Extract data from a RimWorld save file"""

import json
import logging
import time
import xml.etree.ElementTree


def extract_game_version() -> str:
    """Return the base RimWorld game version from the save file's meta element"""
    root = get_save_file_data(save_file_path=get_save_file_path())

    return root.find("./meta/gameVersion").text


def extract_mod_list() -> list:
    """Extracts the list of mods installed in the save game"""
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
    """Recurse through all the data"""
    root = get_save_file_data(save_file_path=get_save_file_path())
    recurse_children(root)


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


def recurse_children(parent) -> None:
    """Recurse through all the children of an element"""
    print(parent.tag, parent.attrib, parent.text)

    for index, child in enumerate(parent):
        recurse_children(child)

        if index >= 10:
            logging.debug("10 siblings belong to parent element have been scanned. Skipping to next\
                 parent node")
            break

    time.sleep(0.01)


if __name__ == "__main__":
    print(f"RimWorld game version: {extract_game_version()}")
    print(f"List of installed mods:\n{json.dumps(extract_mod_list(), indent=4)}")

    if input("Display all game save data? (Y/n) ").upper() == "Y":
        extract_rimworld_save_data()
