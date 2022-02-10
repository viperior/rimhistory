"""Extract XML data from a RimWorld save file and return elements"""

import logging
import pathlib
import xml.etree.ElementTree

import pandas


class Save:
    """Extract the XML data from a RimWorld save file and return the elements"""
    def __init__(self, path_to_save_file: pathlib.Path) -> None:
        """Initialize the Save object by parsing the root XML object using ElementTree

        Parameters:
        path_to_save_file (pathlib.Path): The path to the RimWorld save file to be loaded

        Returns:
        None
        """
        # Parse the XML document and get the root
        self.root = xml.etree.ElementTree.parse(path_to_save_file).getroot()

        # Extract singular data points and sets of data
        self.game_version = self.root.find("./meta/gameVersion").text
        self.mod = {"dictionary_list": self.extract_mod_list()}
        self.pawn = {"dictionary_list": self.extract_pawn_data()}
        self.plant = {"dictionary_list": self.extract_plant_data()}
        self.weather = {"dictionary_list": self.extract_weather_data()}

        # Generate pandas DataFrames from each dataset initialized as a list of dictionaries
        self.generate_dataframes(datasets=[self.mod, self.pawn, self.plant, self.weather])

        # Apply transformations to DataFrames
        self.plant["dataframe"] = self.transform_plant_dataframe(dataframe=self.plant["dataframe"])


    def extract_mod_list(self) -> list:
        """Extract the list of mods installed in the save game

        Parameters:
        None

        Returns:
        list: A list of dictionaries with each installed mod's metadata
        """
        mod_ids = self.root.findall("./meta/modIds")
        mod_steam_ids = self.root.findall("./meta/modSteamIds")
        mod_names = self.root.findall("./meta/modNames")
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


    def extract_weather_data(self) -> dict:
        """Return the weather data for the current map

        Parameters:
        None

        Returns:
        dict: A dictionary containing weather data for the current map
        """
        element = self.root.find(".//weatherManager")
        weather_data = {
            "weather_current": element.find(".//curWeather").text,
            "weather_current_age": element.find(".//curWeatherAge").text,
            "weather_last": element.find(".//lastWeather").text,
        }

        # Nest the weather dictionary inside a list to maintain list of dictionaries as the return
        weather_data_list = [weather_data]

        return weather_data_list


    @staticmethod
    def generate_dataframes(datasets: list) -> None:
        """Generate pandas DataFrames for each input dictionary in the datasets list

        Parameters:
        datasets (list): A list of dictionaries containing a dictionary_list key

        Returns:
        None
        """
        # Validate the input list length
        assert 1 <= len(datasets) <= 100

        logging.debug("Generating pandas DataFrames for %d datasets", len(datasets))

        for dataset in datasets:
            # Validate the input dictionary and keys
            assert isinstance(dataset, dict)
            assert "dictionary_list" in dataset.keys()
            assert "dataframe" not in dataset.keys()

            # Generate the pandas dataframe from the list of dictionaries in dictionary_list
            dataset["dataframe"] = pandas.DataFrame(dataset["dictionary_list"])


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
