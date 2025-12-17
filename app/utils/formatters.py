from typing import List, Dict, Any
from app.utils.logger import get_logger
import json
import re

logger = get_logger("formatters")


def format_assessment_response(assessments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format assessments for API response
    
    Args:
        assessments: List of assessment dictionaries
        
    Returns:
        List[Dict]: Formatted assessments with only required fields
    """
    formatted = []
    
    for assessment in assessments:
        formatted_assessment = {
            "url": assessment.get('url', ''),
            "name": assessment.get('name', ''),
            "adaptive_support": assessment.get('adaptive_support', 'No'),
            "description": assessment.get('description', ''),
            "duration": assessment.get('duration'),
            "remote_support": assessment.get('remote_support', 'No'),
            "test_type": assessment.get('test_type', [])
        }
        formatted.append(formatted_assessment)
    
    return formatted


def extract_json_from_response(response: str) -> dict:
    """
    Robustly extract JSON from LLM response that might contain markdown or extra text
    """
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass
    
    cleaned = response.strip()
    if '```json' in cleaned:
        cleaned = cleaned.split('```json')[1].split('```')[0]
    elif '```' in cleaned:
        cleaned = cleaned.split('```')[1].split('```')[0]
    
    try:
        return json.loads(cleaned.strip())
    except json.JSONDecodeError:
        pass
    
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, response, re.DOTALL)
    
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    array_pattern = r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]'
    matches = re.findall(array_pattern, response, re.DOTALL)
    
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    raise ValueError(f"Could not extract valid JSON from response: {response[:200]}...")


def clean_json_response(response: str) -> str:
    """Clean JSON response by removing markdown formatting"""
    response = response.strip()
    
    if response.startswith("```json"):
        response = response[7:]
    elif response.startswith("```"):
        response = response[3:]
    
    if response.endswith("```"):
        response = response[:-3]
    
    return response.strip()