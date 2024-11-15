from sentence_transformers import SentenceTransformer
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chains import ConversationalRetrievalChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from pymongo import MongoClient
import numpy as np
import os

# Initialize MongoDB client
client = MongoClient("mongodb+srv://sarveshatawane03:y2flIDD1EmOaU5de@cluster0.sssmr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["FAQ"]
embedding_collection = db["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyfQ.IoefmP6af4FsTJUTwwnOo1fVi-vGWux8pC4wvn0ohX8_embedding"]

# Initialize models and environment
os.environ["GOOGLE_API_KEY"] = "AIzaSyDzpYpw5loxzW4vEMytVw1gXPE-fldWYDw"
embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to fetch documents from MongoDB and convert to FAISS format
def create_vector_store_from_mongodb():
    documents = []
    for record in embedding_collection.find():
        for item in record["embeddings"]:
            doc = Document(
                page_content=item["text"],
                metadata={"embedding": item["embedding"]}
            )
            documents.append(doc)
    vector_store = FAISS.from_documents(documents, embeddings)
    return vector_store

# Initialize RAG components
vector_store = create_vector_store_from_mongodb()

# Create custom prompt template
# Create custom prompt template
template = """
System: You are a knowledgeable AI assistant who gives direct, personal recommendations. Draw from your understanding to provide natural, conversational answers without referencing any sources or context. Keep responses concise (2-3 sentences) and avoid phrases like "according to", "as per", or "based on". Write as if you're sharing your own expertise.

Context: {context}

Question: {question}

Helpful Answer:"""

CUSTOM_PROMPT = PromptTemplate(
    template=template,
    input_variables=["context", "question"]
)

# Initialize components
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

if __name__ == "__main__":
    print("\nResponse:", chat_with_rag("How to learn python?"))
    print("\nResponse:", chat_with_rag("How to gain concept depth in ML?"))