"""Test the creation of a plant growth histogram from a pandas DataFrame"""

import os
import pathlib

from save import Save
import view.summary_report


def test_plant_growth_chart(tmp_path: pathlib.Path, test_data_list: list) -> None:
    """Test the creation of a plant growth histogram from a pandas DataFrame

    Parameters:
    tmp_path (pathlib.Path): The path used to stage files needed for testing (fixture)
    test_data_list (list): The list of paths to the test input data files (fixture)

    Returns:
    None
    """
    plant_dataframe = Save(path_to_save_file=test_data_list[0]).data.dataset.plant.dataframe
    labels = {"plant_growth_bin": "Plant growth (%)"}
    plant_growth_chart_html = view.summary_report.get_histogram_html(
        dataframe=plant_dataframe,
        x_axis_field="plant_growth_bin",
        labels=labels
    )
    output_path = tmp_path / "plant_growth_chart.html"

    # Create the HTML file
    with open(output_path, "w", encoding="utf_8") as output_file:
        output_file.write(plant_growth_chart_html)

    # Validate the HTML file's size in bytes
    assert 3000000 <= os.path.getsize(output_path) <= 10000000

    # Validate the HTML content contains the expected boilerplate text from plotly
    with open(output_path, "r", encoding="utf_8") as chart_file:
        assert "plotly.js v" in chart_file.read()
