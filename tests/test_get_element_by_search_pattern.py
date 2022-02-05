"""Test the XML element retrieval functions in extract_save_data"""

import xml.etree.ElementTree

import pytest

import extract.extract_save_data


@pytest.mark.parametrize("search_pattern", [".//world", ".//thing"])
def test_get_element_by_search_pattern(config_data: dict, search_pattern: str) -> None:
    """Test the extract_save_data.get_element_by_search_pattern function

    Parameters:
    config_data (dict): The project configuration data as a dictionary

    Returns:
    None
    """
    save_file_path = config_data["rimworld_save_file_path"]
    tree = xml.etree.ElementTree.parse(save_file_path)
    element = extract.extract_save_data.get_element_by_search_pattern(tree=tree,
        element_search_pattern=search_pattern)

    assert isinstance(element, xml.etree.ElementTree.Element)


@pytest.mark.parametrize("search_pattern", [".//world", ".//thing"])
def test_get_elements_by_search_pattern(config_data: dict, search_pattern: str) -> None:
    """Test the extract_save_data.get_element_by_search_pattern function

    Parameters:
    config_data (dict): The project configuration data as a dictionary
    search_pattern (str): Target XML element search pattern

    Returns:
    None
    """
    save_file_path = config_data["rimworld_save_file_path"]
    tree = xml.etree.ElementTree.parse(save_file_path)
    element_list = extract.extract_save_data.get_elements_by_search_pattern(tree=tree,
        element_search_pattern=search_pattern)

    assert isinstance(element_list, list)
    assert len(element_list) > 0
    assert isinstance(element_list[0], xml.etree.ElementTree.Element)
