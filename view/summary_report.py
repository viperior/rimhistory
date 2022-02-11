"""Generate a summary HTML report for RimWorld save game data"""

import pathlib

import dominate
from dominate.util import raw
from dominate.tags import attr, div, h1, h2, h3, li, link, p, ul
import pandas
import plotly.express

import extract.extract_save_data
from save import Save


def get_environment_section(pawn_data: list, weather_data: dict) -> None:
    """Build the environment and weather section of the report

    Parameters:
    pawn_data (list): The list of dictionaries containing pawn data
    weather_data (dict): A dictionary containing weather data for the map being analyzed

    Returns:
    None
    """
    h2("Environment and Weather")
    h3("Weather")

    with ul():
        li(f"Current weather: {weather_data['weather_current']}")
        li(f"Last weather: {weather_data['weather_last']}")
        li(f"Current weather age: {weather_data['weather_current_age']}")

    h3("Pawn Ambient Temperatures")

    with ul():
        for pawn in pawn_data:
            ambient_temperature = round(float(pawn['pawn_ambient_temperature']), 1)
            ambient_temperature_string = f"{ambient_temperature}&#176;C"
            pawn_temperature_string = f"{ambient_temperature_string} temperature felt by \
                {pawn['pawn_name_full']}"
            li(raw(pawn_temperature_string))


def get_histogram_html(dataframe: pandas.core.frame.DataFrame, x_axis_field: str,
    labels: dict) -> str:
    """Return the HTML for a histogram chart

    Parameters:
    dataframe (pandas.core.frame.DataFrame): The pandas DataFrame to use in the chart
    x_axis_field (str): The field to use for the x-axis series
    labels (dict): A dictionary with the chart labels metadata

    Returns:
    str: A histogram chart HTML
    """
    fig = plotly.express.histogram(dataframe, x=x_axis_field, labels=labels)
    fig.update_layout(bargap=0.05, yaxis_title_text="Count")

    return fig.to_html(full_html=False)


def generate_summary_report(path_to_save_file: pathlib.Path, output_path: pathlib.Path) -> None:
    """Generate an HTML report with a list of the installed mods found

    Parameters:
    path_to_save_file (pathlib.Path): The path to the save file from which to source the data
    output_path (pathlib.Path): The file path where the report should be created

    Returns:
    None
    """
    save = Save(path_to_save_file=path_to_save_file)
    doc = dominate.document(title='RimWorld Save Game Summary Report')

    with doc.head:
        link(rel='stylesheet', href='style.css')

    with doc:
        with div():
            attr(cls='body')
            h1("RimWorld Save Game Summary")
            h2("Game Version")
            p(save.game_version)
            h2("File Size")
            p(f"{extract.extract_save_data.get_save_file_size()} bytes")
            h2(f"Installed Mods ({len(save.mod['dictionary_list'])})")

            with ul():
                for mod in save.mod["dictionary_list"]:
                    mod_list_item_content = mod["mod_name"]
                    mod_steam_id = mod["mod_steam_id"]

                    if mod_steam_id and mod_steam_id != "0":
                        mod_list_item_content += f" (Steam ID: {mod['mod_steam_id']})"

                    li(mod_list_item_content)

            h2(f"Colonists ({len(save.pawn['dictionary_list'])})")

            with ul():
                for pawn in save.pawn["dictionary_list"]:
                    li(f"{pawn['pawn_name_full']}, age {pawn['pawn_biological_age']}")

            h2(f"Plants ({len(save.plant['dictionary_list'])})")

            with ul():
                displayed_plant_types = []

                for plant in save.plant["dictionary_list"]:
                    if plant['plant_definition'] in displayed_plant_types:
                        continue

                    displayed_plant_types.append(plant['plant_definition'])
                    plant_information = (
                        f"{plant['plant_definition']} - "
                        f"{plant['plant_growth']} - "
                        f"{plant['plant_position']}"
                    )
                    li(plant_information)

                    if len(displayed_plant_types) >= 20:
                        break

            plant_dataframe = save.plant["dataframe"]
            p(raw(plant_dataframe.head().to_html()))
            p(raw(plant_dataframe.tail().to_html()))
            p(raw(plant_dataframe.describe().to_html()))
            p(raw(plant_dataframe["plant_definition"].value_counts().to_frame().to_html()))
            raw(
                get_histogram_html(
                    dataframe=plant_dataframe,
                    x_axis_field="plant_growth_bin",
                    labels={"plant_growth_bin": "Plant growth (%)"}
                )
            )
            get_environment_section(
                pawn_data=save.pawn["dictionary_list"],
                weather_data=save.weather["dictionary_list"][0]
            )

    with open(output_path, "w", encoding="utf_8") as output_file:
        output_file.write(str(doc))
