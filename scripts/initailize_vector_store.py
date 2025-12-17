import json
from pathlib import Path   
from app.config import settings
from app.services.vector_store_service import get_vector_store_service
from app.utils.logger import get_logger

logger = get_logger("initialize_vector_store")

async def initialize_vector_store():
    """Initialize vector store with assessments data"""
    try:
        vector_store = get_vector_store_service()
        count = vector_store.chroma_manager.count_documents()
        
        if count > 0:
            logger.info(f"Vector store already initialized with {count} documents")
            return
        
        logger.info("Vector store is empty, initializing with data...")
        assessments_path = Path(settings.ASSESSMENTS_JSON_PATH)
        
        if not assessments_path.exists():
            logger.warning(f"Assessments file not found at {assessments_path}")
            logger.info("Please run the scraper first: python scripts/scrape_catalog.py")
            return
        
        with open(assessments_path, 'r', encoding='utf-8') as f:
            assessments = json.load(f)
        if not assessments or len(assessments) == 0:
            logger.warning("Assessments file is empty")
            logger.info("Please run the scraper first: python scripts/scrape_catalog.py")
            return
        
        logger.info(f"Loading {len(assessments)} assessments from JSON")
        
        indexed_count = await vector_store.index_assessments(assessments)
        
        logger.info(f"Successfully indexed {indexed_count} assessments")
        
    except Exception as e:
        logger.error(f"Failed to initialize vector store: {e}")
        raise