# DocuAI | SaaS Application

---

## Project Objectives and Goals

DocuAI aims to provide a user-friendly SaaS platform for transforming enterprise documents and websites into conversational chatbots without requiring deep knowledge of Retrieval-Augmented Generation or large language models. By automating content ingestion, embedding generation, and search, the platform enables rapid deployment of intelligent chat interfaces through a secure REST API.

## Key Features and Functionalities

- **Secure API Key Authentication**: User registration, login, and OTP-based email verification ensure secure access to chatbot services.
- **Document & Website Ingestion**: Upload PDFs and text files or submit URLs to crawl and extract text, including sublinks, for building a comprehensive knowledge base.
- **Semantic Search & RAG Pipeline**: Leverages sentence-transformer embeddings, MongoDB for vector storage, and LangChain with Gemini LLM to retrieve relevant content and generate conversational responses.
- **Asynchronous Processing**: Utilizes Celery workers to handle heavy tasks (e.g., embedding computation, web crawling) without blocking API responses.
- **Monitoring Dashboard**: Provides real-time insights into API usage, query statistics, and system health for administrators.

## Technology Stack and Frameworks Used

- **Python & FastAPI**: Builds the scalable REST API server.
- **MongoDB**: Stores processed documents, web content, and vector embeddings.
- **PostgreSQL + SQLAlchemy**: Manages user accounts, OTP verification, and API key data.
- **Celery**: Orchestrates background tasks like crawling and embedding generation.
- **LangChain & Gemini (LLM)**: Implements the retrieval-augmented generation workflow, combining embeddings with large language model responses.

## Architecture and Workflow

1. **User Authentication**: Clients register and verify via OTP, receiving an API key.
2. **Content Ingestion**: Users upload documents or URLs. The API enqueues a Celery task for text extraction and embedding computation.
3. **Embedding Storage**: Generated embeddings are stored in MongoDB, indexed for semantic similarity search.
4. **Query Processing**: Upon receiving a chat query, the API retrieves top-k semantically related chunks, then LangChain and Gemini LLM compose the final answer.
5. **Dashboard & Metrics**: All API calls and task statuses are logged, enabling dashboard visualizations of usage and performance.

## Potential Use Cases and Applications

- **Internal Knowledge Bots**: Convert company manuals, policy documents, and training materials into chatbots for employee support.
- **Customer Support Automation**: Provide instant AI-driven responses using product docs and FAQs.
- **Educational Assistants**: Enable students and researchers to query lecture notes, textbooks, or research papers conversationatively.
- **Enhanced Website Search**: Replace keyword-based search with a natural language Q&A interface over website content.

## Summary of Achievements and Skills Demonstrated

- Designed and implemented a multitenant SaaS chatbot platform with secure API key management and OTP-based verification.
- Developed a full RAG pipeline using FastAPI, Celery, MongoDB, and LangChain with a large language model (Gemini).
- Integrated web crawling and document processing workflows to automate knowledge base construction and semantic search.
- Built a real-time monitoring dashboard to track usage metrics and system health.

---

# Technical Documentation

DocuAI is a SaaS platform designed to simplify the process of creating enterprise-grade chatbots. Developers can seamlessly integrate their websites and documents into a chatbot using a secure API key—no prior knowledge of Retrieval-Augmented Generation (RAG) or Large Language Models (LLMs) is required.
Users only need to upload their documents or provide website links, and DocuAI takes care of the rest. It automatically processes the documents and crawls the provided websites, including their sublinks, to extract and embed relevant content for semantic search and chatbot functionality.

To start the project, run the following command:

```bash
./runall.sh
```

---

## Features

- **FastAPI Backend**: Provides REST APIs with secure API key authentication.
- **Web Scraping**: Enables semantic search by uploading websites and processing them with Sentence Transformers for embedding.
- **Secure API Key System**: Includes sample cURL queries for easy integration into developer workflows.
- **Real-Time Monitoring**: Offers an intuitive dashboard to track API calls and query statistics.

---

## Authentication Routes

| Method | Endpoint                     | Description               |
| ------ | ----------------------------- | ------------------------- |
| POST   | `/signin/`                    | Register a new user       |
| POST   | `/login/`                     | Log in a user             |
| POST   | `/verify-otp/`                | Verify email via OTP      |
| POST   | `/resend-verification-email/` | Resend OTP for verification |

---

## User Management Routes

| Method | Endpoint               | Description                |
| ------ | ----------------------- | -------------------------- |
| GET    | `/user-info/`           | Get basic user info        |
| GET    | `/user/details/`        | Get detailed user profile  |
| GET    | `/user-stats/`          | Retrieve usage statistics  |
| PUT    | `/user-stats/update`    | Update user statistics     |
| PUT    | `/user-stats/increment` | Increment usage counters   |
| POST   | `/regenerate-api-key/`  | Regenerate user's API key  |

---

## Query Routes

| Method | Endpoint   | Description                 |
| ------ | ---------- | --------------------------- |
| POST   | `/query`   | Main RAG-based chat endpoint |
| GET    | `/health`  | Health check (heartbeat endpoint) |

---

## Document Management Routes

| Method | Endpoint                | Description                         |
| ------ | ------------------------ | ----------------------------------- |
| POST   | `/doc_upload/`          | Upload documents (PDF, TXT, etc.)   |
| GET    | `/documents/`           | Fetch all uploaded documents        |
| GET    | `/logs/recent_updates/` | Get recent doc uploads             |
| DELETE | `/doc_delete/{doc_id}/` | Delete a document by its ID        |

---

## Web Crawling Routes

| Method | Endpoint                   | Description                        |
| ------ | --------------------------- | ---------------------------------- |
| POST   | `/start-crawl/`            | Start a new web crawl task         |
| GET    | `/crawl-status/{task_id}`  | Check status of crawl task         |
| GET    | `/crawled-content/`        | Retrieve processed crawled data    |

---

## Tech Stack

- **FastAPI** – for backend APIs
- **MongoDB** – for storing documents, crawled content, vector embeddings
- **PostgreSQL / SQLAlchemy** – for user and OTP management
- **Celery** – for async tasks like embedding generation
- **LangChain + Gemini / LLM** – powering the RAG pipeline

---

## Demo Video

[\`Demo_docuai.mp4\`](https://github.com/user-attachments/assets/88d3c040-3970-4cae-b274-6648e9018667)


---
