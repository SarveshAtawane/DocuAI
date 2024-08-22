from tasks import create_vector_embedding, process_all_documents

# To create embedding for a single document
document_id = 'some_document_id'
create_vector_embedding.delay(document_id)

# To process all documents in the collection
process_all_documents.delay()