"""Test the reduce_xml_data function"""

import xml.etree.ElementTree

from save import Save


def test_reduce_xml_data(config_data: dict) -> None:
    """Test the reduce_xml_data function

    Parameters:
    config_data (dict): The project configuration data as a dictionary

    Returns:
    None
    """
    test_tag = "scenario"
    search_pattern = f".//{test_tag}"

    # Test the original tree for one of the items that should be removed
    save = Save(path_to_save_file=config_data["rimworld_save_file_path"])
    input_test_element = save.data.root.find(search_pattern)
    assert isinstance(input_test_element, xml.etree.ElementTree.Element)
    assert input_test_element.tag == test_tag

    # Perform the element removal
    save.data.xml_elements_remove_list.append(search_pattern)
    save.reduce_xml_data()

    # Test the processed version to confirm the successful removal of items
    output_test_element = save.data.root.find(search_pattern)
    assert output_test_element is None
