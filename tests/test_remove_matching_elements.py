"""Test the remove_matching_elements function"""

import xml.etree.ElementTree

import extract.modify_save_file


def test_remove_matching_elements(config_data: dict) -> None:
    """Test the remove_matching_elements function

    Parameters:
    config_data (dict): The project configuration data as a dictionary

    Returns:
    None
    """
    # TODO Parametrize this test case with a list of dictionaries (path, target_tag)
    save_file_path = config_data["rimworld_save_file_path"]
    target_tag = "world"
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
