from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from datetime import datetime
from celery import Celery
from celery.result import AsyncResult
import time
import threading
from DB.mongo import verify_jwt, log_action, db

# Create router and Celery app with Redis result backend
crawler_router = APIRouter()
security = HTTPBearer()
celery_app = Celery(
    'website_crawler',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'  # Added Redis result backend
)

# Configure Celery
celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json']
)

fin = []  # Global list to track URLs (this seems to be a potential debug/placeholder variable)

class CrawlConfig(BaseModel):
    max_pages: int = 50
    exclude_patterns: List[str] = []

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except:
        return False

def is_same_domain(base_url: str, url: str) -> bool:
    try:
        base_domain = urlparse(base_url).netloc
        current_domain = urlparse(url).netloc
        return base_domain == current_domain
    except:
        return False

def fetch_page_content_sync(url: str) -> tuple:
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text(separator='\n', strip=True)
        title = soup.title.string if soup.title else url
        
        return text, title, soup
    except Exception as e:
        logging.error(f"Error fetching {url}: {str(e)}")
        return None, None, None

# New function to periodically poll crawl status
def poll_crawl_status(task_ids: List[str], token: str):
    """
    Periodically poll the status of crawl tasks.
    
    :param task_ids: List of task IDs to monitor
    :param token: User's authentication token
    """
    while task_ids:
        for task_id in task_ids.copy():
            try:
                task_result = AsyncResult(task_id, app=celery_app)
                
                if task_result.ready():
                    # Task is completed
                    print(f"Crawl task {task_id} completed for token {token}")
                    # print(f"Task result: {task_result.result}")
                    
                    # Remove completed task from monitoring list
                    task_ids.remove(task_id)
                else:
                    print(f"Task {task_id} still in progress: {task_result.status}")
            
            except Exception as e:
                logging.error(f"Error checking task status: {str(e)}")
        
        # Wait for a minute before next check
        time.sleep(60)
        
        # Break if all tasks are completed
        if not task_ids:
            break

@celery_app.task(bind=True, name="path.to.process_website_content", queue="crawl_queue")
def process_website_content(self, url: str, token: str, visited_urls: List[str], config: Dict, total_urls: Optional[List[str]] = None):
    try:
        # Update task state to show progress
        self.update_state(state='PROCESSING', meta={'url': url})
        
        collection = db[token]
        text_content, title, soup = fetch_page_content_sync(url)
        
        if not text_content:
            return {
                "status": "failed",
                "error": f"Failed to fetch content from {url}",
                "processed_urls": visited_urls
            }
        website_document = {
            "type": "website_content",
            "url": url,
            "title": title,
            "content": text_content,
            "crawled_at": datetime.utcnow(),
            "metadata": {
                "word_count": len(text_content.split()),
                "character_count": len(text_content)
            }
        }
        
        # Insert the document
        result = collection.insert_one(website_document)
        
        # Log the crawl action
        log_action(token, "website_crawl", {
            "url": url,
            "document_id": str(result.inserted_id),
            "operation": "crawl"
        })
        # Find and queue child pages
        queued_urls = []
        current_count = len(visited_urls)
        if current_count < config['max_pages']:
            for link in soup.find_all('a', href=True):
                child_url = urljoin(url, link['href'])
                if (
                    is_valid_url(child_url) and 
                    is_same_domain(url, child_url) and 
                    child_url not in visited_urls and 
                    not any(pattern in child_url for pattern in config['exclude_patterns'])
                ):
                    visited_urls.append(child_url)
                    queued_urls.append(child_url)
                    if len(visited_urls) >= config['max_pages']:
                        break
                        
            # Queue child pages, passing config for each recursive call
            for child_url in queued_urls:
                print('child_url', child_url)
                fin.append(child_url)
                process_website_content.delay(
                    child_url,
                    token,
                    visited_urls,
                    config,
                    total_urls  # Pass total_urls through
                )
        
        return {
            "status": "success",
            "document_id": str(result.inserted_id),
            "url": url,
            "queued_urls": len(queued_urls),
            "total_urls_processed": len(visited_urls),
            "processed_urls": visited_urls
        }
        
    except Exception as e:
        logging.error(f"Error processing website content: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "url": url,
            "processed_urls": visited_urls
        }

@celery_app.task
def send_crawl_completion_notification(token):
    """
    Optional task to send a notification or perform actions 
    when crawling is complete for a specific token
    """
    try:
        # Example: Could send an email, update a status in database, etc.
        logging.info(f"Crawl completed for token {token}. Sending notification.")
        
        # You could add custom logic here like:
        # - Sending an email
        # - Updating a user dashboard
        # - Triggering post-processing of crawled data
        
    except Exception as e:
        logging.error(f"Error in completion notification: {str(e)}")

@crawler_router.post("/start-crawl/")
async def start_website_crawl(
    config: CrawlConfig,
    token: str = Depends(verify_jwt)
):
    """Start crawling websites stored in MongoDB for the user."""
    try:
        collection = db[token]
        
        # Find all website links stored for the user
        website_docs = collection.find({"type": "website_link"})
        
        # Collect all valid URLs
        all_urls = [doc.get("website_link") for doc in website_docs if is_valid_url(doc.get("website_link"))]
        
        crawl_tasks = []
        for url in all_urls:
            # Start crawling task, passing all URLs for completion tracking
            task = process_website_content.delay(
                url,
                token,
                [url],
                {
                    "max_pages": config.max_pages,
                    "exclude_patterns": config.exclude_patterns
                },
                all_urls  # Pass all URLs to track completion
            )
            crawl_tasks.append({
                "url": url,
                "task_id": task.id
            })
        
        if not crawl_tasks:
            return {"message": "No website links found to crawl"}
        
        # Start a thread to poll task status every minute
        task_ids = [task['task_id'] for task in crawl_tasks]
        polling_thread = threading.Thread(
            target=poll_crawl_status, 
            args=(task_ids, token), 
            daemon=True
        )
        polling_thread.start()
            
        return {
            "message": "Website crawling started",
            "tasks": crawl_tasks
        }
        
    except Exception as e:
        logging.error(f"Error starting crawl: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Rest of the code remains the same (get_crawl_status and get_crawled_content methods)
@crawler_router.get("/crawl-status/{task_id}")
async def get_crawl_status(
    task_id: str,
    token: str = Depends(verify_jwt)
):
    """Get the status of a specific crawl task."""
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        
        if task_result.ready():
            return {
                "task_id": task_id,
                "status": task_result.status,
                "result": task_result.get()
            }
        else:
            return {
                "task_id": task_id,
                "status": task_result.status,
                "info": task_result.info
            }
            
    except Exception as e:
        logging.error(f"Error getting crawl status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@crawler_router.get("/crawled-content/")
async def get_crawled_content(
    token: str = Depends(verify_jwt),
    skip: int = 0,
    limit: int = 10
):
    """Retrieve crawled website content with pagination."""
    try:
        collection = db[token]
        
        # Get total count of crawled pages
        total = collection.count_documents({"type": "website_content"})
        
        # Get paginated results
        crawled_content = collection.find(
            {"type": "website_content"}
        ).skip(skip).limit(limit)
        
        # Format results
        content_list = [{
            "id": str(doc["_id"]),
            "url": doc["url"],
            "title": doc["title"],
            "crawled_at": doc["crawled_at"],
            "metadata": doc.get("metadata", {})
        } for doc in crawled_content]
        
        return {
            "total": total,
            "content": content_list
        }
        
    except Exception as e:
        logging.error(f"Error retrieving crawled content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))