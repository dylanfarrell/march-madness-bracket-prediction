import argparse
from constants import CURRENT_YR


def get_parsed_args():
    # Create the parser
    parser = argparse.ArgumentParser(
        description="""This script scrapes relevant March Madness data. It supports operations for 
        whether to reprocess data, what year to run the scripts for, and whether to overwrite
        existing data."""
    )

    # Add "year" arguments
    parser.add_argument(
        "--year",
        type=int,
        help="Specify the year to process data for. Defaults to the current year.",
        default=CURRENT_YR,
    )

    parser.add_argument(
        "--backfill",
        action="store_true",
        help="Whether to reprocess data or not. Defaults to False.",
        default=False,
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Whether to overwrite the file if it already exists. Defaults to False.",
        default=False,
    )

    # Parse and return the command-line arguments
    return parser.parse_args()
