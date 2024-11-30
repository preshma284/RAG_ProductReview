from data_loader import *
from database_handler import connect_to_db, save_to_db
from vectorization import generate_embeddings, save_embeddings_to_db
import logging
import pandas as pd
import os

# Get the parent directory of the current file's directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(base_dir, 'Amazon-Product-Review-Dataset', 'amazon.csv')
log_file_path = os.path.join(base_dir, 'logs', 'pipeline.log')

# Configure logging to write to a file
# Ensure the logs directory exists
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Clear existing handlers (if any) to avoid conflicts
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configure logging to write to a file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()  # Optional: Also log to console
    ]
)

logger = logging.getLogger(__name__)


def run_pipeline():

    #Load data
    mongo_uri = 'mongodb://localhost:27017/'
    db_name = 'product-review-data1'
    collection_name = 'product_reviews8'
    expected_columns = ['product_id', 'product_name', 'category', 'discounted_price', 'actual_price', 'discount_percentage', 'rating', 'rating_count', 'about_product', 'user_id', 'user_name', 'review_id', 'review_title', 'review_content', 'img_link', 'product_link']  # Example schema

    try:
        #Run data loader.py
        data = load_data(file_path)
        print("Data loaded successfully.")
        logging.info("Data loaded successfully.")

        #Validate schema
        validate_schema(data, expected_columns)
        logging.info("Schema validation passed.")

        #Profile data
        profile_data(data)

        #Run data handler.py
        cleaned_data = clean_data(data)
        print("Data cleaned successfully.")
        logging.info("Data cleaned successfully.")

        #Save data to the db
        db = connect_to_db(mongo_uri, db_name)
        save_to_db(cleaned_data, db, collection_name)
        logging.info("Data saved to MongoDB successfully.")
        print("Data saved to database successfully.")

        # Retrieve data with _id from MongoDB
        retrieved_data = pd.DataFrame(list(db[collection_name].find()))
        logging.info("Cleaned data retrieved from MongoDB successfully.")

        # Generate embeddings for the retrieved data
        data_with_embeddings = generate_embeddings(retrieved_data, 'review_content')
        save_embeddings_to_db(data_with_embeddings, db, collection_name)
        logging.info("Embeddings saved to MongoDB successfully.")

    except FileNotFoundError as e:
        logger.error("File not found: %s", e, exc_info=True)
    except ValueError as e:
        logger.error("Value error: %s", e, exc_info=True)
    except pd.errors.ParserError as e:
        logger.error("Pandas parser error: %s", e, exc_info=True)
    except ConnectionError as e:
        logger.error("Database connection error: %s", e, exc_info=True)
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e, exc_info=True)



if __name__ == '__main__':
    run_pipeline()
