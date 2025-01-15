from sentence_transformers import SentenceTransformer
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chains import ConversationalRetrievalChain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from pymongo import MongoClient
import os

# Initialize MongoDB client
uri = "mongodb+srv://sarveshatawane03:y2flIDD1EmOaU5de@cluster0.sssmr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)
db = client["FAQ"]
embedding_collection = db["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxfQ.K5HH2dyajgarHqfXmv7Ate12h1dx3VGQD1MHNdKkq5I_embedding"]

# Initialize models and environment
os.environ["GOOGLE_API_KEY"] = "AIzaSyB6g2_uoe8VcchVeXMZ06rJJe0Qawle-vU"
embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to fetch documents from MongoDB and convert to FAISS format
def create_vector_store_from_mongodb():
    documents = []

    print("Fetching documents from MongoDB...")
    # print(embedding_collection.find())
    for record in embedding_collection.find():
        # print(record)
        embeddings_array = record.get("embeddings", [])
        for embedding_object in embeddings_array:
            text = embedding_object.get("text")
            embedding = embedding_object.get("embedding")
            if text and embedding:  # Ensure both text and embedding exist
                doc = Document(page_content=text, metadata={"embedding": embedding})
                documents.append(doc)

    if not documents:
        raise ValueError("No valid documents found in MongoDB.")

    # Debug: Check the number of valid documents
    print(f"Number of valid documents: {len(documents)}")

    # Generate FAISS vector store
    vector_store = FAISS.from_documents(documents, embeddings)
    return vector_store


# Initialize RAG components
vector_store = create_vector_store_from_mongodb()

# Create custom prompt template
template = """
System: You are [ENTITY_NAME]'s knowledgeable and friendly virtual assistant. Engage with users naturally, as if you're having a conversation, while accurately conveying information about [ENTITY_NAME], its services, and related topics. You should:

- Speak naturally and conversationally, avoiding phrases like "based on the provided text" or "the context shows"
- Give comprehensive, informative answers that flow naturally
- Use a warm, helpful tone while maintaining professionalism
- Share relevant details that might interest the user
- Ask clarifying questions when needed
- If you can't provide complete information about something, be honest and explain what you do know

Context: {context}

User: {question}
"""

CUSTOM_PROMPT = PromptTemplate(
    template=template,
    input_variables=["context", "question"]
)

# Initialize components
from langchain_google_genai import ChatGoogleGenerativeAI  # Ensure this package is installed
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
retriever = vector_store.as_retriever()
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Create ConversationalRetrievalChain with custom prompt
conversational_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    combine_docs_chain_kwargs={"prompt": CUSTOM_PROMPT}
)

# Function to chat with the RAG system
def chat_with_rag(user_input):
    try:
        response = conversational_chain({"question": user_input})
        
        print("\nChat History:")
        for message in memory.chat_memory.messages:
            print(f"{message.type}: {message.content}")
        
        return response["answer"]
    except Exception as e:
        return f"Error processing request: {str(e)}"

# Main entry point
if __name__ == "__main__":
    print("\nResponse:", chat_with_rag("What are some mainboard current ipo?"))
    print("\nResponse:", chat_with_rag("What is sme?"))
