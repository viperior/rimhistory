"""Test the reduce_xml_data function"""

import json
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
    save = Save(
        path_to_save_file=config_data["rimworld_save_file_path"],
        reduce_xml=False,
        preserve_root=True
    )
    input_test_element = save.data.root.find(search_pattern)
    assert isinstance(input_test_element, xml.etree.ElementTree.Element)
    assert input_test_element.tag == test_tag

    # Get the list of XPath patterns to use for element removal
    with open("defaults.json", "r", encoding="utf_8") as defaults_file:
        defaults_data = json.load(defaults_file)

    xml_remove_list = defaults_data["xml_elements_remove_list"]

    # Create a new save object with the element removed and test
    xml_remove_list.append(search_pattern)
    save_reduced = Save(
        path_to_save_file=config_data["rimworld_save_file_path"],
        reduce_xml=True,
        xml_remove_list=xml_remove_list,
        preserve_root=True
    )

    # Test the reduced save to confirm the successful removal of items
    output_test_element = save_reduced.data.root.find(search_pattern)
    assert output_test_element is None
