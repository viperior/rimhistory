"""Generate a summary HTML report for RimWorld save game data"""

import pathlib

import dominate
from dominate.util import raw
from dominate.tags import attr, div, h1, h2, h3, li, link, p, ul
import pandas
import plotly.express

from save import SaveSeries


def get_environment_section(series: SaveSeries) -> None:
    """Build the environment and weather section of the report

    Parameters:
    series (SaveSeries): The SaveSeries object containing the plant data

    Returns:
    None
    """
    weather_df = series.data.weather
    pawn_df = series.latest_save.data.pawn
    h2("Environment and Weather")
    h3("Weather")

    with ul():
        li(f"Current weather: {weather_df['weather_current']}")
        li(f"Last weather: {weather_df['weather_last']}")
        li(f"Current weather age: {weather_df['weather_current_age']}")

    h3("Pawn Ambient Temperatures")

    with ul():
        for _, pawn in pawn_df.iterrows():
            ambient_temperature = round(float(pawn['pawn_ambient_temperature']), 1)
            ambient_temperature_string = f"{ambient_temperature}&#176;C"
            pawn_temperature_string = f"{ambient_temperature_string} temperature felt by \
                {pawn['pawn_name_full']}"
            li(raw(pawn_temperature_string))


def get_histogram_html(df: pandas.core.frame.DataFrame, x_axis_field: str, labels: dict) -> str:
    """Return the HTML for a histogram chart

    Parameters:
    df (pandas.core.frame.DataFrame): The pandas DataFrame to use in the chart
    x_axis_field (str): The field to use for the x-axis series
    labels (dict): A dictionary with the chart labels metadata

    Returns:
    str: A histogram chart HTML
    """
    fig = plotly.express.histogram(df, x=x_axis_field, labels=labels)
    fig.update_layout(bargap=0.05, yaxis_title_text="Count")

    return fig.to_html(full_html=False)


def generate_summary_report(save_dir_path: pathlib.Path, file_regex_pattern: str,
                            output_path: pathlib.Path) -> None:
    """Generate an HTML report with a list of the installed mods found

    Parameters:
    save_dir_path (pathlib.Path): The directory where the series of RimWorld save files is stored
    file_regex_pattern (str): The regex pattern used to select a set of matching RimWorld save files
    output_path (pathlib.Path): The file path where the report should be created

    Returns:
    None
    """
    series = SaveSeries(
        save_dir_path=save_dir_path,
        save_file_regex_pattern=file_regex_pattern
    )
    save = series.latest_save
    doc = dominate.document(title='RimWorld Save Game Summary Report')
    current_pawn_df = save.data.pawn.query("(current_record == True) and \
                                           (is_humanoid_colonist == True)")
    current_pawn_df.reset_index(drop=True, inplace=True)

    with doc.head:
        link(rel='stylesheet', href='style.css')

    with doc:
        with div():
            attr(cls='body')
            h1("RimWorld Save Game Summary")
            h2("Game Version")
            p(save.data.game_version)
            h2("File Size")
            p(f"{save.data.file_size} bytes")
            h2(f"Installed Mods ({len(save.data.mod.index)})")

            with ul():
                for _, mod in save.data.mod.iterrows():
                    mod_list_item_content = mod["mod_name"]
                    mod_steam_id = mod["mod_steam_id"]

                    if mod_steam_id and mod_steam_id != "0":
                        mod_list_item_content += f" (Steam ID: {mod['mod_steam_id']})"

                    li(mod_list_item_content)

            h2(f"Colonists ({len(current_pawn_df.index)})")

            with ul():
                for _, pawn in current_pawn_df.iterrows():
                    li(f"{pawn['pawn_name_full']}, age {pawn['pawn_biological_age']}")

            get_plant_section(series=series)
            get_environment_section(series=series)

    with open(output_path, "w", encoding="utf_8") as output_file:
        output_file.write(str(doc))


def get_plant_section(series: SaveSeries) -> None:
    """Build the plant section of the report

    Parameters:
    series (SaveSeries): The SaveSeries object containing the plant data

    Returns:
    None
    """
    current_plant_df = series.latest_save.data.plant
    series_plant_df = series.data.plant
    h2(f"Plants ({len(current_plant_df.index)})")

    with ul():
        displayed_plant_types = []

        for _, plant in current_plant_df.iterrows():
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

    plant_df = current_plant_df
    p(raw(plant_df.head().to_html()))
    p(raw(plant_df.tail().to_html()))
    p(raw(plant_df.describe().to_html()))
    p(raw(plant_df["plant_definition"].value_counts().to_frame().to_html()))
    raw(
        get_histogram_html(
            df=plant_df,
            x_axis_field="plant_growth_bin",
            labels={"plant_growth_bin": "Plant growth (%)"}
        )
    )
    p(raw(series_plant_df.head().to_html()))
    p(raw(series_plant_df.tail().to_html()))
    p(raw(series_plant_df.describe().to_html()))

    # Plant chart #1 - Total population
    plant_agg_df = series_plant_df\
        .groupby(["time_ticks"])\
        .agg({"plant_id": "count"})
    fig = plotly.express.line(
        plant_agg_df,
        title="Plant population over time",
        markers=True,
        labels={"time_ticks": "Time", "plant_id": "Plant population"}
    )
    raw(fig.to_html(full_html=False))

    # Plant chart #2 - By species
    plant_agg_by_species_df = series_plant_df[
        ["time_ticks", "plant_definition", "plant_id"]
    ]
    plant_agg_by_species_df = plant_agg_by_species_df\
        .groupby(["time_ticks", "plant_definition"])\
        .agg({"plant_id": "count"})\
        .reset_index()
    fig = plotly.express.line(
        plant_agg_by_species_df,
        x="time_ticks",
        y="plant_id",
        title="Plant population by species over time",
        markers=True,
        color="plant_definition",
        labels={"time_ticks": "Time", "plant_id": "Plant population"}
    )
    raw(fig.to_html(full_html=False))
