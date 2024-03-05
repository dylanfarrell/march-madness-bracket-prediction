import numpy as np
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
from constants import SPORTS_REF_STUB, CURRENT_YR

from argparser_config import get_parsed_args
import helper_functions as hf


def create_team_stats(yr: int = CURRENT_YR, overwrite: bool = False):
    link = f"{SPORTS_REF_STUB}/cbb/seasons/men/{yr}-school-stats.html"
    with urllib.request.urlopen(link) as url:
        page = url.read()
    soup = BeautifulSoup(page, "html.parser")

    schools_data = []

    # Identify the header row to get column names (excluding the first "Rk" and last "School" headers as they're processed separately)
    header_row = soup.find("thead").find_all("tr")[
        1
    ]  # Assuming the second row in thead is the relevant one
    column_names = [header.text for header in header_row.find_all("th")][
        1:
    ]  # Skip 'Rk', include 'School' and onwards

    # Find the table body
    table_body = soup.find("tbody")
    if table_body:
        # Find all rows in the table body
        rows = table_body.find_all("tr")
        for row in rows:
            row_data = {}
            # Extracting School Name and ID
            school_tag = row.find("a")
            if school_tag:
                school_name = school_tag.text
                school_id = school_tag["href"].split("/")[3]  # Extract school ID
                row_data["School Name"] = school_name
                row_data["school_id"] = school_id
            # Extracting other columns
            data_points = row.find_all("td")
            for column_name, data_point in zip(column_names, data_points):
                # print(column_name)
                row_data[column_name] = data_point.text.strip()
            schools_data.append(row_data)

    # Display the data
    for school in schools_data:
        print(school)

    df = pd.DataFrame(schools_data, columns=["school_id"] + column_names)
    df = df.dropna(subset=["School"]).reset_index(drop=True)

    file_path = f"{hf.get_generated_dir(yr)}/sports_reference_team_stats.csv"
    hf.write_to_csv(df, file_path, overwrite)

    all_schools = get_all_schools(df)
    all_schools = pd.DataFrame(all_schools, columns=["school_id"])
    all_schools.to_pickle(f"{hf.get_generated_dir(yr)}/all_schools.pkl")


def get_all_schools(df):
    return list(df["school_id"].unique())


def main():
    # Parse the command-line arguments
    args = get_parsed_args()

    # Call the function with the command-line arguments
    create_team_stats(yr=args.year, overwrite=args.overwrite)


if __name__ == "__main__":
    main()
