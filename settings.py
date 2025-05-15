import os

# Base project directory (root of the project)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to the dataset directory
DATA_DIR = os.path.join(BASE_DIR, "dataset")

# Path to the n-gram dataset file
NGRAM_DATASET_PATH = os.path.join(DATA_DIR, "1grams_time_cols.pkl")

# Path to the cache directory
CACHE_DIR = os.path.join(BASE_DIR, "cache")