"""Extract XML data from a RimWorld save file and return elements"""

import pathlib
import xml.etree.ElementTree


class Save:
    """Extract the XML data from a RimWorld save file and return the elements"""
    def __init__(self, path_to_save_file: pathlib.Path) -> None:
        """Initialize the Save object by parsing the root XML object using ElementTree

        Parameters:
        path_to_save_file (pathlib.Path): The path to the RimWorld save file to be loaded

        Returns:
        None
        """
        self._root = xml.etree.ElementTree.parse(path_to_save_file).getroot()
        self._pawn = self.extract_pawn_data()


    def extract_pawn_data(self) -> list:
        """Return a list of dictionaries containing pawn data

        Parameters:
        None

        Returns:
        list: The list of dictionaries containing pawn data
        """
        pawn_data_elements = self.root.findall(".//li[@Class='Tale_SinglePawn']")
        pawn_data = []

        for element in pawn_data_elements:
            current_pawn = {
                "pawn_id": element.find(".//pawnData/pawn").text,
                "pawn_name_first": element.find(".//pawnData/name/first").text,
                "pawn_name_nick": element.find(".//pawnData/name/nick").text,
                "pawn_name_last": element.find(".//pawnData/name/last").text,
                "pawn_biological_age": element.find(".//pawnData/age").text,
                "pawn_chronological_age": element.find(".//pawnData/chronologicalAge").text,
                "pawn_ambient_temperature": element.find(".//surroundings/temperature").text,
            }
            current_pawn["pawn_name_full"] = (
                f"{current_pawn['pawn_name_first']} "
                f"\"{current_pawn['pawn_name_nick']}\" "
                f"{current_pawn['pawn_name_last']}"
            )
            pawn_data.append(current_pawn)

        return pawn_data


    @property
    def pawn(self) -> list:
        """Return a list of dictionaries containing pawn data"""
        return self._pawn


    @property
    def root(self):
        """Return the root XML element of the RimWorld save file (.rws file extension)"""
        return self._root
