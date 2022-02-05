"""Test the XML element retrieval functions in extract_save_data"""

import xml.etree.ElementTree

import extract.extract_save_data


def test_get_element_by_search_pattern(config_data: dict) -> None:
    """Test the extract_save_data.get_element_by_search_pattern function

    Parameters:
    config_data (dict): The project configuration data as a dictionary

    Returns:
    None
    """
    search_pattern = ".//world"
    # TODO Change this test case to be parametrized and add additional search patterns as test input
    save_file_path = config_data["rimworld_save_file_path"]
    tree = xml.etree.ElementTree.parse(save_file_path)
    element = extract.extract_save_data.get_element_by_search_pattern(tree=tree,
        element_search_pattern=search_pattern)

    assert isinstance(element, xml.etree.ElementTree.Element)
