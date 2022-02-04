"""Test the modify_save_file.find_target_element function"""

import xml.etree.ElementTree

import extract.modify_save_file


def test_modify_save_file() -> None:
    """Test the modify_save_file.find_target_element function

    Parameters:
    None

    Returns:
    None
    """
    search_pattern = ".//world"

    # TODO After refactor/rename of the function is complete, test this to ensure it works
    # TODO Change this test case to be parametrized and add additional search patterns as test input
    element = extract.modify_save_file.find_target_element(search_pattern)

    assert isinstance(element, xml.etree.ElementTree.Element)
