"""Test the XML element retrieval functions in extract_save_data"""

import xml.etree.ElementTree

import pytest

import extract.extract_save_data


def get_search_patterns() -> list:
    """Return a list of search patterns to use as test input data

    Parameters:
    None

    Returns:
    list: A list of XPath search patterns
    """
    return [".//world", ".//thing"]


@pytest.mark.parametrize("search_pattern", get_search_patterns())
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


@pytest.mark.parametrize("search_pattern", get_search_patterns())
def test_get_elements_by_search_pattern(config_data: dict, search_pattern: str) -> None:
    """Test the extract_save_data.get_elements_by_search_pattern function

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


@pytest.mark.parametrize("search_pattern", get_search_patterns())
def test_get_elements_by_search_pattern_with_limit(config_data: dict, search_pattern: str) -> None:
    """Test the extract_save_data.get_elements_by_search_pattern function using the limit parameter

    Parameters:
    config_data (dict): The project configuration data as a dictionary
    search_pattern (str): Target XML element search pattern

    Returns:
    None
    """
    save_file_path = config_data["rimworld_save_file_path"]
    tree = xml.etree.ElementTree.parse(save_file_path)
    element_list = extract.extract_save_data.get_elements_by_search_pattern(tree=tree,
        element_search_pattern=search_pattern, limit=3)

    assert isinstance(element_list, list)
    assert len(element_list) > 0
    assert isinstance(element_list[0], xml.etree.ElementTree.Element)
