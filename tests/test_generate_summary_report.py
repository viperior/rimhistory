"""Test the view.summary_report.generate_summary_report function"""

import view.summary_report


def test_generate_summary_report() -> None:
    """Test the view.summary_report.generate_summary_report function

    Parameters:
    None

    Returns:
    None
    """
    # FIXME Build out the logic of this test case to finalize this contribution
    # It should do more than generate the report. It should also test the generated report.
    report_output_directory = "data/reports"
    report_file_name_base = "summary_report"
    view.summary_report.generate_summary_report(output_directory=report_output_directory,
        output_file_name=report_file_name_base)
