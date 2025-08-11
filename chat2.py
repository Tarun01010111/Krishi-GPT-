import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import AI packages, continue without them if they fail
try:
    from langchain_together import Together
    from langchain.chains import RetrievalQA
    from langchain.prompts import PromptTemplate
    AI_PACKAGES_AVAILABLE = True
    logger.info("LangChain packages loaded successfully")
except ImportError as e:
    logger.warning(f"LangChain packages not available: {e}")
    AI_PACKAGES_AVAILABLE = False
    # Create dummy classes
    class Together:
        def __init__(self, *args, **kwargs):
            pass
    class RetrievalQA:
        @staticmethod
        def from_chain_type(*args, **kwargs):
            return None
    class PromptTemplate:
        def __init__(self, *args, **kwargs):
            pass

# Initialize the language model
if AI_PACKAGES_AVAILABLE:
    try:
        llm = Together(
            model="meta-llama/Llama-2-70b-chat-hf",
            max_tokens=512,
            temperature=0.1,
            top_k=1,
            together_api_key=os.getenv("TOGETHER_API_KEY", "YOUR_Together_API_KEY")
        )
        logger.info("Together AI LLM initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Together AI: {e}")
        llm = None
else:
    llm = None

# Set up the retrieval QA chain
def setup_retrieval_qa(db):
    if not AI_PACKAGES_AVAILABLE or llm is None:
        logger.warning("AI packages or LLM not available, cannot setup retrieval QA")
        return None
        
    try:
        if db is None:
            raise ValueError("Database is None")
            
        retriever = db.as_retriever(similarity_score_threshold=0.6)

        # Define the prompt template
        prompt_template = """ Your name is AgriGenius, Please answer questions related to Agriculture. Try explaining in simple words. Answer in less than 100 words. If you don't know the answer, simply respond with 'Don't know.'
         CONTEXT: {context}
         QUESTION: {question}"""

        PROMPT = PromptTemplate(template=f"[INST] {prompt_template} [/INST]", input_variables=["context", "question"])

        # Initialize the RetrievalQA chain
        chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type='stuff',
            retriever=retriever,
            input_key='query',
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT},
            verbose=True
        )
        return chain
    except Exception as e:
        logger.error(f"Error setting up retrieval QA: {str(e)}")
        return None
