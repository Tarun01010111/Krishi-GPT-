import requests
import PyPDF2
from itertools import chain
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import AI packages, continue without them if they fail
try:
    from langchain_community.vectorstores import Chroma
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.embeddings import HuggingFaceEmbeddings
    AI_PACKAGES_AVAILABLE = True
    logger.info("AI packages loaded successfully")
except ImportError as e:
    logger.warning(f"AI packages not available: {e}")
    AI_PACKAGES_AVAILABLE = False
    # Create dummy classes
    class Chroma:
        @staticmethod
        def from_texts(*args, **kwargs):
            return None
    class RecursiveCharacterTextSplitter:
        def __init__(self, *args, **kwargs):
            pass
        def split_text(self, text):
            return [text[i:i+500] for i in range(0, len(text), 500)]
    class HuggingFaceEmbeddings:
        def __init__(self, *args, **kwargs):
            pass

# Function to fetch content from a website
def fetch_website_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.text
    except requests.RequestException as e:
        logger.error(f"Error fetching content from {url}: {str(e)}")
        return ""

# Function to extract text from a PDF file
def extract_pdf_text(pdf_file):
    try:
        with open(pdf_file, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text()
        return text
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_file}: {str(e)}")
        return ""

# Split the combined content into smaller chunks
def split_text(text, chunk_size=500, chunk_overlap=100):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_text(text)
    return chunks

# Initialize embeddings and vector store
def initialize_vector_store(contents):
    if not AI_PACKAGES_AVAILABLE:
        logger.warning("AI packages not available, skipping vector store initialization")
        return None
        
    try:
        # Use a simpler, more memory-efficient embedding model
        embedding_function = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True, 'batch_size': 8}  # Smaller batch size
        )
        
        # Filter out empty contents
        valid_contents = [content for content in contents if content.strip()]
        if not valid_contents:
            logger.warning("No valid content found to initialize vector store")
            return None
        
        web_chunks = []
        for content in valid_contents:
            chunks = split_text(content, chunk_size=200, chunk_overlap=20)  # Much smaller chunks
            web_chunks.extend(chunks[:20])  # Limit to first 20 chunks per content
        
        if not web_chunks:
            logger.warning("No chunks generated from content")
            return None
        
        # Limit total chunks to avoid memory issues
        web_chunks = web_chunks[:50]  # Process only first 50 chunks total
        logger.info(f"Processing {len(web_chunks)} text chunks")
            
        db = Chroma.from_texts(web_chunks, embedding_function)
        return db
    except Exception as e:
        logger.error(f"Error initializing vector store: {str(e)}")
        return None
