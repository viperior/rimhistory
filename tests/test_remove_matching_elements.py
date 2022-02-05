"""Test the remove_matching_elements function"""

import xml.etree.ElementTree

import pytest

import extract.modify_save_file


@pytest.mark.parametrize("target_tag", ["world", "playerFaction"])
def test_remove_matching_elements(config_data: dict, target_tag: str) -> None:
    """Test the remove_matching_elements function

    Parameters:
    config_data (dict): The project configuration data as a dictionary
    target_tag (str): The XML tag type to remove from the tree

    Returns:
    None
    """
    save_file_path = config_data["rimworld_save_file_path"]
    remove_element_pattern = f".//{target_tag}"
    tree = xml.etree.ElementTree.parse(save_file_path)
    root = tree.getroot()
    target_element = root.find(remove_element_pattern)

    # Test for the presence of the target element before attempting to remove it
    assert isinstance(target_element, xml.etree.ElementTree.Element)
    assert target_element.tag == target_tag

    # Remove the target element
    modified_tree = extract.modify_save_file.remove_matching_elements(tree=tree,
        search_pattern=remove_element_pattern)

    # Test for the successful removal of the target element
    modified_root = modified_tree.getroot()
    modified_target_element = modified_root.find(remove_element_pattern)

    assert modified_target_element is None
