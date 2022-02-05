"""Test the XML element retrieval functions in extract_save_data"""

import json
import xml.etree.ElementTree

import extract.extract_save_data


def test_get_element_by_search_pattern() -> None:
    """Test the extract_save_data.get_element_by_search_pattern function

    Parameters:
    None

    Returns:
    None
    """
    search_pattern = ".//world"

    # TODO Change this test case to be parametrized and add additional search patterns as test input
    with open("config.json", "r", encoding="utf_8") as config_file:
        config_data = json.load(config_file)

    save_file_path = config_data["rimworld_save_file_path"]
    tree = xml.etree.ElementTree.parse(save_file_path)
    element = extract.extract_save_data.get_element_by_search_pattern(tree=tree,
        element_search_pattern=search_pattern)

    assert isinstance(element, xml.etree.ElementTree.Element)
