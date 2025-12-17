"""
Run script for Chainlit application
"""
import subprocess
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from app.config import settings
from app.utils.logger import get_logger
from app.database import init_db, init_chroma
from scripts.initailize_vector_store import initialize_vector_store
from app.services.vector_store_service import get_vector_store_service
logger = get_logger("run_chainlit")

async def pre_initialize_system():
    """Pre-initialize system before starting Chainlit"""
    try:
        logger.info("Initializing databases...")
        init_db()
        init_chroma()
        logger.info("Databases initialized")
        
        logger.info("Checking vector store...")
        vector_store = get_vector_store_service()
        count = vector_store.chroma_manager.count_documents()
        
        if count > 0:
            logger.info(f"Vector store already contains {count} documents")
            logger.info("=" * 30)
            return True
        
        logger.info("Vector store is empty, loading assessments...")
        logger.info("This will take 1-2 minutes to generate embeddings...")
        
        await initialize_vector_store()
        count = vector_store.chroma_manager.count_documents()
        
        if count > 0:
            logger.info(f"Successfully indexed {count} assessments")
            logger.info("=" * 60)
            return True
        else:
            logger.error("=" * 60)
            logger.error("Vector store initialization failed - no documents indexed")
            logger.error("Please run the scraper first: python scripts/scrape_catalog.py")
            return False
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"Initialization failed: {e}")
        logger.error("=" * 60)
        return False


def main():
    """Main entry point"""
    print("=" * 30)
    print("Starting SHL Assessment Recommendation System - Chainlit UI")
    print(f"Host: {settings.CHAINLIT_HOST}")
    print(f"Port: {settings.CHAINLIT_PORT}")
    print("=" * 30)
    logger.info("Checking system initialization...")
    success = asyncio.run(pre_initialize_system())
    
    if not success:
        logger.error("=" * 30)
        logger.error("Failed to initialize system")
        logger.error("=" * 30)
        sys.exit(1)
    
    print()
    logger.info("=" * 30)
    logger.info("Starting Chainlit application...")
    logger.info("=" * 30)

    subprocess.run([
        "chainlit",
        "run",
        "chainlit_app/app.py",
        "--host", settings.CHAINLIT_HOST,
        "--port", str(settings.CHAINLIT_PORT)
    ])


if __name__ == "__main__":
    main()