"""Test the extract_save_data.get_element_by_search_pattern function"""

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

    # TODO After refactor/rename of the function is complete, test this to ensure it works
    # TODO Change this test case to be parametrized and add additional search patterns as test input
    element = extract.extract_save_data.get_element_by_search_pattern(search_pattern)

    assert isinstance(element, xml.etree.ElementTree.Element)
