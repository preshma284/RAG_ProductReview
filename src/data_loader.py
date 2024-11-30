#Data Ingestion

import pandas as pd
import logging
import re
import emoji

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_data(file_path):
    try:
        # Load the CSV file
        data = pd.read_csv(file_path)
        logging.info("Data loaded successfully from %s", file_path)
        return data
    except Exception as e:
        logging.error("Error loading data: %s", e)
        raise

def validate_schema(data, expected_columns):
    # Validate the schema of the loaded data
    if list(data.columns) != expected_columns:
        raise ValueError(f"Schema mismatch. Expected columns: {expected_columns}, but got: {list(data.columns)}")
    logging.info("Schema validation passed.")


def clean_data(data):
    try:

        for column in data.columns:
            if data[column].dtype == 'object':
                data[column] = data[column].fillna('Unknown')
                logging.info("Missing values in column '%s' filled with 'Unknown'.", column)
            elif pd.api.types.is_numeric_dtype(data[column]):
                data[column] = data[column].fillna(data[column].mean())
                logging.info("Missing values in column '%s' filled with mean value.", column)
            elif pd.api.types.is_datetime64_any_dtype(data[column]):
                data[column] = data[column].fillna(pd.Timestamp('1970-01-01'))
                logging.info("Missing values in column '%s' filled with '1970-01-01'.", column)


        # # Drop missing values
        # data = data.dropna()
        # logging.info("Missing values dropped.")

        # Remove duplicates
        data = data.drop_duplicates()
        logging.info("Duplicates removed.")

        # Normalize text
        if 'review_content' in data.columns:
            data['review_content'] = data['review_content'].str.lower().str.strip()
            data['review_content'] = data['review_content'].apply(lambda x: re.sub(r'[^\w\s]', '', x))  # Remove punctuation
            # Remove emojis from the review content
            data['review_content'] = data['review_content'].apply(lambda x: emoji.replace_emoji(x, replace=''))
            logging.info("Text data normalized.")

        # Convert data types if necessary
        # Example: Convert 'date' column to datetime
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
            logging.info("Date column converted to datetime.")

        return data
    except Exception as e:
        logging.error("Error cleaning data: %s", e)
        raise

def profile_data(data):
    # data profiling
    logging.info("Data profiling:")
    logging.info("Number of rows: %d", len(data))
    logging.info("Number of columns: %d", len(data.columns))
    logging.info("Column data types:\n%s", data.dtypes)
    logging.info("Missing values:\n%s", data.isnull().sum())
