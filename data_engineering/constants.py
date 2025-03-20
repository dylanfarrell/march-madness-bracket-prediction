# Years
CURRENT_YR = 2025
DATA_START_YR = 2003

# Directories
KAGGLE_DIR = f"../data/{CURRENT_YR}/kaggle_data"
KAGGLE_DIR_LAST_YR = f"../data/{CURRENT_YR - 1}/kaggle_data"
GENERATED_DIR = f"../data/{CURRENT_YR}/generated_data"
GENERATED_DIR_LAST_YR = f"../data/{CURRENT_YR - 1}/generated_data"
KAGGLE_DIR = f"../data/{CURRENT_YR}/silver_data"

# Sports Reference
SPORTS_REF_STUB = "https://www.sports-reference.com"

MENS_GENERATED_DATASETS = [
    "coaches_data",
    "preseason_rankings",
    "returning_player_team_stats_tourney",
    "sports_ref_team_stats",
    "team_weighted_info_tourney",
    "stationary_probabilities",
]

# For now, not all scraped Men's data is available on the Women's side
WOMENS_GENERATED_DATASETS = [
    "coaches_data",
    "preseason_rankings",
    "sports_ref_team_stats",
    "stationary_probabilities",
]

MODE_DIRECTORY = {"M": "mens", "W": "womens"}
