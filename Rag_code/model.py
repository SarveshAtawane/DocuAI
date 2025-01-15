import logging
from sentence_transformers import SentenceTransformer
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chains import ConversationalRetrievalChain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pymongo import MongoClient
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("rag_model.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RAGModel:
    def __init__(self):
        try:
            # Initialize MongoDB connection
            logger.info("Initializing MongoDB connection...")
            self.uri = "mongodb+srv://sarveshatawane03:y2flIDD1EmOaU5de@cluster0.sssmr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
            self.client = MongoClient(self.uri)
            self.db = self.client["FAQ"]

            # Initialize models and environment
            logger.info("Setting up models and environment...")
            os.environ["GOOGLE_API_KEY"] = "AIzaSyB6g2_uoe8VcchVeXMZ06rJJe0Qawle-vU"
            self.embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
            self.model = SentenceTransformer('all-MiniLM-L6-v2')

            # Initialize conversation components
            self.initialize_conversation_chain()

        except Exception as e:
            logger.error(f"Error initializing RAGModel: {e}")
            raise

    def create_vector_store_from_mongodb(self, token: str):
        try:
            documents = []
            # Construct collection name using the token from API params
            collection_name = token
            self.embedding_collection = self.db[collection_name]
            logger.info(f"Using MongoDB collection: {collection_name}")

            for record in self.embedding_collection.find():
                embeddings_array = record.get("embeddings", [])
                for embedding_object in embeddings_array:
                    text = embedding_object.get("text")
                    embedding = embedding_object.get("embedding")
                    if text and embedding:
                        doc = Document(page_content=text, metadata={"embedding": embedding})
                        documents.append(doc)

            if not documents:
                raise ValueError("No valid documents found in MongoDB.")

            logger.info("Successfully created vector store.")
            return FAISS.from_documents(documents, self.embeddings)

        except Exception as e:
            logger.error(f"Error creating vector store from MongoDB: {e}")
            raise

    def initialize_conversation_chain(self):
        try:
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
            logger.info("Initializing prompt template...")
            self.prompt = PromptTemplate(
                template=template,
                input_variables=["context", "question"]
            )

            # Initialize LLM and memory
            logger.info("Initializing LLM...")
            self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )

        except Exception as e:
            logger.error(f"Error initializing conversation components: {e}")
            raise

    def chat_with_rag(self, query: str, entity_name: str, token: str) -> str:
        try:
            # Create vector store and conversation chain for this specific request
            logger.info(f"Creating vector store for token: {token}")
            vector_store = self.create_vector_store_from_mongodb(token)
            
            # Create conversation chain with the new vector store
            conversation_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=vector_store.as_retriever(),
                memory=self.memory,
                combine_docs_chain_kwargs={"prompt": self.prompt}
            )

            # Process the chat request
            logger.info(f"Processing chat request for query: {query} and entity: {entity_name}")
            response = conversation_chain({
                "question": query
            })
            logger.info(f"Received response: {response}")
            return response["answer"]
        except Exception as e:
            logger.error(f"Error processing chat request: {e}")
            raise Exception(f"Error processing chat request: {str(e)}")

    def __del__(self):
        try:
            logger.info("Closing MongoDB connection...")
            self.client.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Example usage