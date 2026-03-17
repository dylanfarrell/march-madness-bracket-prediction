import argparse
from constants import CURRENT_YR


def get_parser() -> argparse.ArgumentParser:
    # Create the parser
    parser = argparse.ArgumentParser(
        description="""This script scrapes relevant March Madness data. It supports operations for 
        whether to reprocess data, what year to run the scripts for, and whether to overwrite
        existing data."""
    )

    parser.add_argument(
        "--year",
        type=int,
        help="Specify the year to process data for. Defaults to the current year.",
        default=CURRENT_YR,
    )

    parser.add_argument(
        "--mode",
        type=str,
        help="Run in Women's mode (W) or Men's mode (M). Defaults to M for backwards compatability for now",
        default="M",
    )

    parser.add_argument(
        "--recompute",
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

    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Flag for testing a dataflow for a one-off year. Defaults to False.",
        default=False,
    )

    # return the command-line arguments unparsed
    return parser
