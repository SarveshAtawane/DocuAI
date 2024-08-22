from celery_config import app
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer  # You may need to install this

# MongoDB connection
client = MongoClient('your_mongodb_uri')
db = client['your_database_name']
collection = db['your_collection_name']

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')  # You can choose a different model

@app.task
def create_vector_embedding(document_id):
    # Retrieve document from MongoDB
    document = collection.find_one({'_id': document_id})
    
    if not document:
        return f"Document {document_id} not found"

    # Create embedding
    text = document.get('text', '')  # Adjust based on your document structure
    embedding = model.encode(text).tolist()  # Convert numpy array to list for MongoDB storage

    # Update document with embedding
    collection.update_one(
        {'_id': document_id},
        {'$set': {'vector_embedding': embedding}}
    )

    return f"Created embedding for document {document_id}"

@app.task
def process_all_documents():
    document_ids = [doc['_id'] for doc in collection.find({}, {'_id': 1})]
    for doc_id in document_ids:
        create_vector_embedding.delay(doc_id)
    return f"Queued {len(document_ids)} documents for embedding creation"