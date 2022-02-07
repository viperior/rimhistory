"""Extract data from a RimWorld save file"""

import json
import logging
import os
import xml.etree.ElementTree

import pandas


def extract_game_version() -> str:
    """Return the base RimWorld game version from the save file's meta element

    Parameters:
    None

    Returns:
    str: The full game version as a human-friendly string
    """
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


def get_element_by_search_pattern(tree: xml.etree.ElementTree, element_search_pattern: str) ->\
    xml.etree.ElementTree.Element:
    """Search for an XML element in a RimWorld save file using a search pattern

    Parameters:
    tree (xml.etree.ElementTree): The XML tree to search
    element_search_pattern (str): Target element search pattern

    Returns:
    xml.etree.ElementTree.Element: The first instance of the element matching the search pattern
    """
    logging.debug("Searching for element using pattern: %s", element_search_pattern)
    root = tree.getroot()
    element = root.find(element_search_pattern)
    logging.debug("Element information:\nTag: %s\nAttributes: %s\nText: %s\nKeys: %s",
        element.tag, element.attrib, element.text, element.keys())

    return element


def get_elements_by_search_pattern(tree: xml.etree.ElementTree, element_search_pattern: str,
    limit: int=None) -> list:
    """Search for an XML element in a RimWorld save file using a search pattern

    Parameters:
    tree (xml.etree.ElementTree): The XML tree to search
    element_search_pattern (str): Target element search pattern
    limit (int): The maximum number of matching elements to return (default None)

    Returns:
    list: A list of XML elements matching the search pattern
    """
    logging.debug("Searching for all elements using pattern: %s", element_search_pattern)
    root = tree.getroot()
    elements = root.findall(element_search_pattern)
    element_list = []

    for element in elements:
        logging.debug("Element information:\nTag: %s\nAttributes: %s\nText: %s\nKeys: %s",
            element.tag, element.attrib, element.text, element.keys())
        element_list.append(element)

        # Enforce limit
        if limit is not None:
            if len(element_list) >= limit:
                logging.debug("Stopping returning additional elements due to having reached the \
                    limit of elements to return (%d)", limit)
                break

    return element_list


def get_element_lineage(element: xml.etree.ElementTree.Element,
    root: xml.etree.ElementTree.Element, lineage: str=None) -> str:
    """Return the lineage of an element as a string showing the hierarchy of tags going back to the
    root element of the XML document

    Parameters:
    element (xml.etree.ElementTree.Element): The element being analyzed
    root (xml.etree.ElementTree.Element): The root element of the XML document
    lineage (str): The string representation of the element hierarchy

    Returns:
    str: String representation of the lineage of the XML element
    """

    # Add the starting element to the lineage string
    if lineage is None:
        logging.debug("Initializing the lineage string with the starting element")
        lineage = element.tag

    # Check to see if the element has a parent element
    parent = root.find(f".//{element.tag}/..")

    # The top level has been reached. End recursion by returning the lineage data
    if parent is None:
        logging.debug("Tag lineage analysis is complete. Returning lineage:\n%s", lineage)
        return lineage

    # This block only executes when there is a valid parent
    logging.debug("The current element, %s, has a parent element, %s.\nRecursing XML tree",
        element.tag, parent.tag)

    # Prepend the detected parent to the lineage string
    lineage = f"{parent.tag} > {lineage}"

    # Recurse upward in the hierarchy, eventually returning the complete hierarchy
    return get_element_lineage(element=parent, root=root, lineage=lineage)


def get_pawn_count() -> int:
    """Return the number of pawns detected in the save game data

    Parameters:
    tree (xml.etree.ElementTree): The XML tree to search

    Returns:
    int: The number of pawns found in the XML data
    """
    target_tag = "pawnData"
    root = get_save_file_data(get_save_file_path())
    pawn_data_elements = root.findall(f".//{target_tag}")

    return len(list(pawn_data_elements))


def get_pawn_data() -> list:
    """Return a list of dictionaries containing data about the pawns extracted from the save file

    Parameters:
    None

    Returns:
    None
    """
    target_tag = "pawnData"
    root = get_save_file_data(get_save_file_path())
    pawn_data_elements = root.findall(f".//{target_tag}")
    pawn_data = []

    for element in pawn_data_elements:
        current_pawn = {
            "pawn_id": element.find(".//pawn").text,
            "pawn_name_first": element.find(".//first").text,
            "pawn_name_nick": element.find(".//nick").text,
            "pawn_name_last": element.find(".//last").text,
            "pawn_biological_age": element.find(".//age").text,
            "pawn_chronological_age": element.find(".//chronologicalAge").text,
        }
        current_pawn["pawn_name_full"] = (
            f"{current_pawn['pawn_name_first']} "
            f"\"{current_pawn['pawn_name_nick']}\" "
            f"{current_pawn['pawn_name_last']}"
        )
        pawn_data.append(current_pawn)

    return pawn_data


def get_plant_count() -> int:
    """Return the number of plants identified in the save game file

    Parameters:
    None

    Returns:
    int: The number of plants identified in the save game file
    """
    search_pattern = ".//thing[@Class='Plant']"
    root = get_save_file_data(get_save_file_path())
    xml_elements = root.findall(search_pattern)
    element_count = 0

    for index, element in enumerate(xml_elements):
        if index % 1000 == 0:
            logging.debug("Loading data from element #%d: %s", index,
                get_element_lineage(element=element, root=root))

        element_count += 1

    return element_count


def get_plant_data() -> list:
    """Return a list of dictionaries containing data about the plants extracted from the save file

    Parameters:
    None

    Returns:
    None
    """
    search_pattern = ".//thing[@Class='Plant']"
    root = get_save_file_data(get_save_file_path())
    xml_elements = root.findall(search_pattern)
    return_data = []

    for element in xml_elements:
        current_element_data = {
            "plant_id": element.find(".//id").text,
            "plant_definition": element.find(".//def").text,
            "plant_map_id": element.find(".//map").text,
            "plant_position": element.find(".//pos").text,
            "plant_growth": element.find(".//growth").text,
            "plant_age": element.find(".//age").text,
        }
        return_data.append(current_element_data)

    return return_data


def get_save_file_data(save_file_path: str) -> xml.etree.ElementTree.Element:
    """Return the root element from the RimWorld save game XML data

    Parameters:
    save_file_path (str): The path to the save file as a string

    Returns:
    xml.etree.ElementTree.Element: The save data XML tree's root element
    """
    tree = xml.etree.ElementTree.parse(save_file_path)
    root = tree.getroot()

    return root


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


def plant_dataframe() -> pandas.core.frame.DataFrame:
    """Convert a list of dictionaries with plant data to a pandas DataFrame

    Parameters:
    list: The list of dictionaries containing plant data

    Returns:
    pandas.core.frame.DataFrame: A dataframe containing the plant data
    """
    return pandas.DataFrame(data=get_plant_data())


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
