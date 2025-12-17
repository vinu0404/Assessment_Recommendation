from app.database.sqlite_db import get_db
from app.utils.logger import get_logger

logger = get_logger("api_dependencies")


def get_db_session():
    """
    Dependency to get database session
    
    Yields:
        Database session
    """
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()