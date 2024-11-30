# Amazon Product Review Pipeline

This repository contains a data pipeline for processing Amazon product reviews. The pipeline includes data loading, cleaning, validation, profiling, and embedding generation, and it saves the processed data to a MongoDB database.

## Project Structure

amazon-product-review-pipeline

 src
 data_loader.py         # Functions for loading and validating data
 database_handler.py    # Functions for connecting to MongoDB and saving data
 vectorization.py       # Functions for generating embeddings
 pipeline.py            # Main script to run the data pipeline
 api.py                 # Flask API for querying processed data

 requirements.txt           # Python dependencies
 pipeline.log               # Log file for execution details
 LICENSE                    # License file
 README.md                  # Documentation


## Setup

### Prerequisites

- Python 3.8 or higher
- MongoDB

### Installation

1. Clone the repository:

```sh
    git clone https://github.com/yourusername/amazon-product-review-pipeline.git
    cd amazon-product-review-pipeline
```

2. Create and activate a virtual environment:

```sh
    python -m venv venv
    venv\Scripts\activate
```

3. Install the required packages:

```sh
    pip install -r requirements.txt
```

### Environment Variables

Set the following variables:

1. **GROQ_API_KEY**: Your Groq API key.
2. **MONGODB_URI**: The URI for your MongoDB instance.
3. **DATABASE_NAME**: The name of the MongoDB database.
4. **COLLECTION_NAME**: The name of the MongoDB collection.

#### Setting Environment Variables on Windows
#### Groq API Key Integration
**Command Prompt**:
```sh
set GROQ_API_KEY="your_api_key_here"
```


####  MongoDB Setup
#### Updating Database Connection Details

Ensure that the MongoDB server is running and update the MongoDB connection details in the following files if necessary:

src/pipeline.py
src/api.py


####  Running the Pipeline

1. Run the Data Pipeline
      To execute the pipeline:
**command prompt**:
```sh
python src/pipeline.py
```

This command will load data from amazon.csv, process it, and save the results to the MongoDB database. Check the pipeline.log file for detailed execution logs and error tracking.

2. Run the Flask API
   To start the API server:
**command prompt**:
```sh
python src/api.py
```

The API will be accessible at http://localhost:5000. Use this endpoint to interact with the processed data using POST request from postman or cURL by passing query in json format

**bash**:
```sh
curl -X POST http://127.0.0.1:5000/query      -H "Content-Type: application/json"      -d '{"query": "What do people think about Wayona charging cable?"}'
```

#### Logging
Logs are configured to be written to both the console and a file located at pipeline.log.
Refer to this log file for detailed execution information and debugging purposes.




