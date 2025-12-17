import re
from typing import List, Optional
from validators import url as validate_url_validator
from app.utils.logger import get_logger


logger = get_logger("validators")

def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid URL
    
    Args:
        url: URL string to validate
        
    Returns:
        bool: True if valid URL, False otherwise
    """
    try:
        return validate_url_validator(url) is True
    except Exception as e:
        logger.warning(f"URL validation error for {url}: {e}")
        return False


def validate_query_length(query: str, min_length: int = 10, max_length: int = 10000) -> tuple[bool, Optional[str]]:
    """
    Validate query length
    
    Args:
        query: Query string to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, "Query cannot be empty"
    
    query_length = len(query.strip())
    
    if query_length < min_length:
        return False, f"Query is too short. Minimum {min_length} characters required."
    
    if query_length > max_length:
        return False, f"Query is too long. Maximum {max_length} characters allowed."
    
    return True, None


def extract_urls_from_text(text: str) -> List[str]:
    """
    Extract all URLs from a text string
    
    Args:
        text: Text containing potential URLs
        
    Returns:
        List[str]: List of extracted URLs
    """
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    
    urls = re.findall(url_pattern, text)
    valid_urls = [url for url in urls if validate_url(url)]
    
    logger.debug(f"Extracted {len(valid_urls)} valid URLs from text")
    
    return valid_urls

