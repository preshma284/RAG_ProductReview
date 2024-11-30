from sentence_transformers import SentenceTransformer

def generate_embeddings(data, text_column):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    data['embeddings'] = data[text_column].apply(lambda x: model.encode(x))
    return data


def save_embeddings_to_db(data, db, collection_name):
    collection = db[collection_name]
    for index, row in data.iterrows():
        try:
            # Ensure embeddings are JSON-serializable
            embeddings_list = [float(val) for val in row['embeddings']]
            
            # Verify that _id exists
            if '_id' not in row:
                raise KeyError("_id is missing in the DataFrame row.")

            # Update the document with the new embeddings
            result = collection.update_one(
                {'_id': row['_id']},
                {'$set': {'embeddings': embeddings_list}}
            )

            # Log the update status
            if result.matched_count == 0:
                print(f"No document found with _id {row['_id']}")
            else:
                print(f"Updated document with _id {row['_id']} successfully.")

        except Exception as e:
            print(f"Error updating document with _id {row.get('_id', 'N/A')}: {e}")
