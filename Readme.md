# DocuAI | SaaS Application  

DocuAI is a SaaS platform designed to simplify the process of creating enterprise-grade chatbots. Developers can seamlessly integrate their websites and documents into a chatbot using a secure API key—no prior knowledge of Retrieval-Augmented Generation (RAG) or Large Language Models (LLMs) is required.  

Users only need to upload their documents or provide website links, and DocuAI takes care of the rest. It automatically processes the documents and crawls the provided websites, including their sublinks, to extract and embed relevant content for semantic search and chatbot functionality.  

To start the project, run the following command:  
```bash
./runall.sh
```

---

## 🚀 Features  

- **FastAPI Backend**: Provides REST APIs with secure API key authentication.  
- **Web Scraping**: Enables semantic search by uploading websites and processing them with Sentence Transformers for embedding.  
- **Secure API Key System**: Includes sample cURL queries for easy integration into developer workflows.  
- **Real-Time Monitoring**: Offers an intuitive dashboard to track API calls and query statistics.  

---

## 🔐 Authentication Routes  

| Method | Endpoint                          | Description                          |  
|--------|-----------------------------------|--------------------------------------|  
| POST   | `/signin/`                        | Register a new user                  |  
| POST   | `/login/`                         | Log in a user                        |  
| POST   | `/verify-otp/`                    | Verify email via OTP                 |  
| POST   | `/resend-verification-email/`     | Resend OTP for verification          |  

---

## 👤 User Management Routes  

| Method | Endpoint                          | Description                          |  
|--------|-----------------------------------|--------------------------------------|  
| GET    | `/user-info/`                     | Get basic user info                  |  
| GET    | `/user/details/`                  | Get detailed user profile            |  
| GET    | `/user-stats/`                    | Retrieve usage statistics            |  
| PUT    | `/user-stats/update`              | Update user statistics               |  
| PUT    | `/user-stats/increment`           | Increment usage counters             |  
| POST   | `/regenerate-api-key/`            | Regenerate user's API key            |  

---

## 💬 Query Routes  

| Method | Endpoint   | Description                                  |  
|--------|------------|----------------------------------------------|  
| POST   | `/query`    | Main RAG-based chat endpoint                 |  
| GET    | `/health`  | Health check (heartbeat endpoint)            |  

---

## 📄 Document Management Routes  

| Method | Endpoint                    | Description                              |  
|--------|-----------------------------|------------------------------------------|  
| POST   | `/doc_upload/`              | Upload documents (PDF, TXT, etc.)        |  
| GET    | `/documents/`               | Fetch all uploaded documents             |  
| GET    | `/logs/recent_updates/`     | Get recent doc uploads                   |  
| DELETE | `/doc_delete/{doc_id}/`     | Delete a document by its ID              |  

---

## 🌐 Web Crawling Routes  

| Method | Endpoint                         | Description                              |  
|--------|----------------------------------|------------------------------------------|  
| POST   | `/start-crawl/`                  | Start a new web crawl task               |  
| GET    | `/crawl-status/{task_id}`        | Check status of crawl task               |  
| GET    | `/crawled-content/`              | Retrieve processed crawled data          |  

---

## 🛠 Tech Stack  

- **FastAPI** – for backend APIs  
- **MongoDB** – for storing documents, crawled content, vector embeddings  
- **PostgreSQL / SQLAlchemy** – for user and OTP management  
- **Celery** – for async tasks like embedding generation  
- **LangChain + Gemini / LLM** – powering the RAG pipeline  

## 🎥 Demo Video

https://github.com/user-attachments/assets/88d3c040-3970-4cae-b274-6648e9018667



---

## 📬 Contact  

For issues, suggestions, or contributions, feel free to open an issue or PR.  
