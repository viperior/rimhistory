"""Test the view.summary_report.generate_summary_report function"""

import logging

import view.summary_report


def test_generate_summary_report() -> None:
    """Test the view.summary_report.generate_summary_report function

    Parameters:
    None

    Returns:
    None
    """
    # Parameters
    report_output_directory = "data/reports"
    report_file_name_base = "summary_report"

    # Generate the report
    view.summary_report.generate_summary_report(output_directory=report_output_directory,
        output_file_name=report_file_name_base)
    output_path = f"{report_output_directory}/{report_file_name_base}.html"

    # Test the generated report
    with open(output_path, "r", encoding="utf_8") as report_file:
        doctype = report_file.readline()

        # Check for a DOCTYPE tag on the first line
        assert "DOCTYPE" in doctype
        minimum_line_count_sentry = False

        for line_counter, line in enumerate(report_file):
            # Log the XML line data every 10th line at the DEBUG level
            if line_counter % 10 == 0:
                logging.debug(line)

            # The report XML should have at least 20 lines of content
            if line_counter >= 20:
                minimum_line_count_sentry = True

    # Check whether the generated file exceeds a minimum line length threshold
    assert minimum_line_count_sentry is True
