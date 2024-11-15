from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import os

# Set Google API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyDzpYpw5loxzW4vEMytVw1gXPE-fldWYDw"

# Read the data
with open('data.txt', 'r', encoding='utf-8') as file:
    text_data = file.read()
text_chunks = text_data.split('\n\n')
documents = [Document(page_content=chunk) for chunk in text_chunks]

# Initialize Gemini embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Create vector store
vector_store = FAISS.from_documents(documents, embeddings)

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
retriever = vector_store.as_retriever()

# Initialize conversation memory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Create ConversationalRetrievalChain
conversational_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory
)

# Function to handle user input and get responses
def chat_with_rag(user_input):
    response = conversational_chain({"question": user_input})
    print("\nChat History:")
    for message in memory.chat_memory.messages:
        print(f"{message.type}: {message.content}")
    return response["answer"]

# Example conversation
print("Response:", chat_with_rag("What is this text about?"))
print("\nResponse:", chat_with_rag("What is his CGPA?"))
print("\nResponse:", chat_with_rag("Can you provide more details about his performance?"))