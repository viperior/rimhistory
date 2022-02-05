"""Utilities to perform modifications to a RimWorld save file (XML)"""
import json
import logging
import os
import xml.etree.ElementTree

import tqdm


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


def process_save_file(input_file_path: str, output_file_path: str, xml_elements_remove_list: list)\
    -> None:
    """Process a raw RimWorld game save file by removing unnecessary information

    Parameters:
    input_file_path (str): The path to the save file to process
    output_file_path (str): The path to store the modified XML data
    xml_elements_remove_list (list): A list of XPath patterns to use to remove matching XML elements

    Returns:
    None
    """
    tree = xml.etree.ElementTree.parse(input_file_path)

    for search_pattern in tqdm.tqdm(xml_elements_remove_list):
        logging.debug("Removing XML elements matching search pattern: %s", search_pattern)
        tree = remove_matching_elements(tree=tree, search_pattern=search_pattern)

    tree.write(output_file_path)
    input_file_size = os.path.getsize(input_file_path)
    output_file_size = os.path.getsize(output_file_path)
    size_difference = input_file_size - output_file_size
    size_difference_percent = round((size_difference / input_file_size) * 100, 2)
    logging.debug("Input file size = %d\nOutput file size = %d\nFile size reduced by %d (%.2f%%)",
        input_file_size, output_file_size, size_difference, size_difference_percent)


def process_save_file_user_prompt() -> None:
    """Prompt the user for instructions on whether and how to process their game save file

    Parameters:
    None

    Returns:
    None
    """
    process_file_prompt = "Do you want to process your save file? (Y/n) "

    if input(process_file_prompt).upper() == "Y":
        processing_method_prompt = "1 - Use paths from config.json\n2 - Enter custom paths now\n"
        processing_method_response = int(input(processing_method_prompt))

        if processing_method_response == 1:
            process_save_file_using_config()
        elif processing_method_response == 2:
            input_file_path = input("Input file path: ")
            output_file_path = input("Output file path: ")

            with open("defaults.json", "r", encoding="utf_8") as defaults_file:
                defaults_data = json.load(defaults_file)

            xml_elements_remove_list = defaults_data["xml_elements_remove_list"]
            process_save_file(input_file_path=input_file_path, output_file_path=output_file_path,
                xml_elements_remove_list=xml_elements_remove_list)


def process_save_file_using_config() -> None:
    """Process a raw RimWorld game save file using the paths configured in config.json

    Parameters:
    None

    Returns:
    None
    """
    logging.basicConfig(filename="modify_save_file.log", encoding="utf_8", level=logging.INFO)

    with open("config.json", "r", encoding="utf_8") as config_file:
        config_data = json.load(config_file)

    rimworld_save_file_path = config_data["rimworld_save_file_path"]
    processed_file_path = config_data["processed_save_file_path"]

    with open("defaults.json", "r", encoding="utf_8") as defaults_file:
        defaults_data = json.load(defaults_file)

    xml_elements_remove_list = defaults_data["xml_elements_remove_list"]

    process_save_file(
        input_file_path=rimworld_save_file_path,
        output_file_path=processed_file_path,
        xml_elements_remove_list=xml_elements_remove_list
    )


def remove_matching_elements(tree: xml.etree.ElementTree, search_pattern: str, limit: int=None) ->\
    xml.etree.ElementTree:
    """ Remove XML elements matching the given search pattern

    Parameters:
    tree (xml.etree.ElementTree): The XML tree to modify
    search_pattern (str): The XPath search pattern to use to find matching elements in the tree
    limit (int): The maximum number of matching elements to remove (default None)

    Returns:
    xml.etree.ElementTree: The XML tree with the matching elements removed
    """
    elements_removed_count = 0
    sentry = True

    while sentry:
        root = tree.getroot()
        element = root.find(search_pattern)
        starting_element_removed_count = elements_removed_count

        if element is None:
            logging.debug("Element matching pattern (%s) not found", search_pattern)
        else:
            logging.debug("Element matching pattern found: %s; Targeting parent element",
                element.tag)
            parent_element_search_pattern = f"{search_pattern}/.."
            parent = root.find(parent_element_search_pattern)

            if parent is None:
                logging.error("Unexpected error occurred when trying to lookup parent element\n\
                    Search pattern used: %s", parent_element_search_pattern)
            else:
                logging.debug("Parent element found. Proceeding with removal of child element")
                parent.remove(element)
                elements_removed_count += 1

        # If no element was removed, stop trying to remove new occurrences
        if elements_removed_count == starting_element_removed_count:
            sentry = False

        # Enforce limit
        if limit is not None:
            if elements_removed_count >= limit:
                logging.debug("Stopping removal of additional elements (%s) due to having reached \
                    the limit of elements to remove (%d)", element.tag, limit)
                sentry = False

    logging.debug("%d elements removed total", elements_removed_count)

    return tree


if __name__ == "__main__":
    process_save_file_user_prompt()
