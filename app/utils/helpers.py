import re
from typing import List, Dict, Any, Optional
from app.utils.logger import get_logger

logger = get_logger("helpers")


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""

    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
    
    return text.strip()



def extract_duration_from_text(text: str) -> Optional[int]:
    """
    Extract duration requirement from text
    
    Args:
        text: Text containing duration information
        
    Returns:
        Optional[int]: Duration in minutes
    """
    patterns = [
        r'(\d+)\s*(?:minutes?|mins?)',
        r'(\d+)\s*(?:hours?|hrs?)',
        r'about\s+(\d+)\s*(?:minutes?|mins?)',
        r'(?:at most|maximum|max)\s+(\d+)\s*(?:minutes?|mins?)',
    ]
    
    text_lower = text.lower()
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            value = int(match.group(1))
            if 'hour' in match.group(0) or 'hr' in match.group(0):
                value *= 60
            
            return value
    
    return None


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List[List]: Chunked list
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
