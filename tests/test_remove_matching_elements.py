"""Test the remove_matching_elements function"""

import xml.etree.ElementTree

import pytest

from save import Save


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
    save = Save(path_to_save_file=save_file_path, preserve_root=True)
    target_element = save.data.root.find(remove_element_pattern)

    # Test for the presence of the target element before attempting to remove it
    assert isinstance(target_element, xml.etree.ElementTree.Element)
    assert target_element.tag == target_tag

    # Remove the target element
    save.remove_matching_elements(search_pattern=remove_element_pattern)

    # Test for the successful removal of the target element
    modified_target_element = save.data.root.find(remove_element_pattern)

    assert modified_target_element is None
