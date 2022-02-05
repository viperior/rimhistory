"""Utilities to perform modifications to a RimWorld save file (XML)"""
import logging
import os
import xml.etree.ElementTree

import tqdm


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
            assert isinstance(parent, xml.etree.ElementTree.Element)

            if parent is not None:
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
