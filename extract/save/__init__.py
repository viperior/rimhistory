"""Extract XML data from a RimWorld save file and return elements"""

import pathlib
import xml.etree.ElementTree

import pandas


class Dataset:
    """Work with sets of data from RimWorld save files (.rws) using lists and pandas DataFrames"""
    def __init__(self, source_dictionary_list: list) -> None:
        """Initialize the Dataset object

        Parameters:
        source_dictionary_list (list): The list of dictionaries containing the raw data

        Returns:
        None
        """
        self._dictionary_list = source_dictionary_list[:]
        self._dataframe = pandas.DataFrame(self._dictionary_list)


    @property
    def dataframe(self) -> pandas.core.frame.DataFrame:
        """Return a pandas DataFrame containing the data"""
        return self._dataframe


    @dataframe.setter
    def dataframe(self, dataframe: pandas.core.frame.DataFrame) -> None:
        """Setter function for the dataframe property"""
        self._dataframe = dataframe


    @property
    def dictionary_list(self) -> list:
        """Return a list of dictionaries containing the data"""
        return self._dictionary_list


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
        self._mod = Dataset(source_dictionary_list=self.extract_mod_list())
        self._pawn = Dataset(source_dictionary_list=self.extract_pawn_data())
        self._plant = Dataset(source_dictionary_list=self.extract_plant_data())
        self._plant.dataframe = self.transform_plant_dataframe(dataframe=self._plant.dataframe)


    def extract_mod_list(self) -> list:
        """Extract the list of mods installed in the save game

        Parameters:
        None

        Returns:
        list: A list of dictionaries with each installed mod's metadata
        """
        mod_ids = self._root.findall("./meta/modIds")
        mod_steam_ids = self._root.findall("./meta/modSteamIds")
        mod_names = self._root.findall("./meta/modNames")
        mod_list = []

        for index, mod_id in enumerate(mod_ids[0]):
            mod_info = {
                "mod_id": mod_id.text,
                "mod_name": mod_names[0][index].text,
                "mod_steam_id": mod_steam_ids[0][index].text
            }
            mod_list.append(mod_info)

        return mod_list


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


    def extract_plant_data(self) -> list:
        """Return a list of dictionaries containing plant data"""
        search_pattern = ".//thing[@Class='Plant']"
        xml_elements = self.root.findall(search_pattern)
        plant_data = []

        for element in xml_elements:
            current_element_data = {
                "plant_id": element.find(".//id").text,
                "plant_definition": element.find(".//def").text,
                "plant_map_id": element.find(".//map").text,
                "plant_position": element.find(".//pos").text,
                "plant_growth": element.find(".//growth").text,
                "plant_age": element.find(".//age").text,
            }
            plant_data.append(current_element_data)

        return plant_data


    @property
    def game_version(self) -> str:
        """Return the base RimWorld game version as a string from the save file's meta element"""
        return self.root.find("./meta/gameVersion").text


    @property
    def mod(self) -> Dataset:
        """Return a list of dictionaries containing mod data"""
        return self._mod


    @staticmethod
    def transform_plant_dataframe(dataframe: pandas.core.frame.DataFrame) ->\
        pandas.core.frame.DataFrame:
        """Transform the plants DataFrame by adding calculated columns

        Parameters:
        dataframe (pandas.core.frame.DataFrame): The original pandas DataFrame with plant data

        Returns:
        pandas.core.frame.DataFrame: The modified DataFrame
        """
        # Create a column by converting plant_growth to a float and multiplying it by 100
        dataframe["plant_growth_percentage"] = dataframe["plant_growth"].astype(float) * 100

        # Bin the percentage values in ranges for visualization and summarized reporting
        bins = range(0, 101, 5)
        dataframe["plant_growth_bin"] = pandas.cut(dataframe["plant_growth_percentage"], bins,
            labels=bins[1:])

        return dataframe


    @property
    def pawn(self) -> Dataset:
        """Return a list of dictionaries containing pawn data"""
        return self._pawn


    @property
    def plant(self) -> Dataset:
        """Return a list of dictionaries containing plant data"""
        return self._plant


    @property
    def root(self) -> xml.etree.ElementTree.Element:
        """Return the root XML element of the RimWorld save file (.rws file extension)"""
        return self._root
