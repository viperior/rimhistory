"""Test the get_element_lineage function"""

import logging
import xml.etree.ElementTree

import pytest

import extract.modify_save_file


@pytest.mark.parametrize(
    "target_tag,expected",
    [
        ("world", "savegame > game > world"),
        ("thing", "savegame > meta > modIds > li > things > thing")
    ]
)
def test_get_element_lineage(config_data: dict, target_tag: str, expected: str) -> None:
    """Test the get_element_lineage function

    Parameters:
    config_data (dict): The project configuration data as a dictionary
    target_tag (str): The XML tag type to use to fetch the lineage
    expected (str): The expected test result

    Returns:
    None
    """
    tree = xml.etree.ElementTree.parse(config_data["rimworld_save_file_path"])
    root = tree.getroot()
    element = root.find(f".//{target_tag}")
    logging.debug("Determining the lineage of XML tag: %s", element.tag)
    lineage = extract.modify_save_file.get_element_lineage(element=element, root=root)
    logging.debug("Element lineage = %s", lineage)

    assert lineage == expected
