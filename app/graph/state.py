from typing import TypedDict, List, Dict, Any, Optional
from app.models.schemas import EnhancedQuery


class GraphState(TypedDict):
    """State structure for the LangGraph workflow"""
    query: str
    session_id: str
    intent: Optional[str]
    intent_confidence: Optional[float]
    has_url: bool
    extracted_urls: List[str]
    jd_text: Optional[str]
    jd_extraction_success: bool
    enhanced_query: Optional[EnhancedQuery]
    retrieved_assessments: List[Dict[str, Any]]
    final_recommendations: List[Dict[str, Any]]
    general_answer: Optional[str]
    error_message: Optional[str]
    processing_steps: List[str]
    agent_outputs: Dict[str, Any]


def create_initial_state(query: str, session_id: str) -> GraphState:
    """
    Create initial graph state
    
    Args:
        query: User query
        session_id: Session identifier
        
    Returns:
        Initial graph state
    """
    return GraphState(
        query=query,
        session_id=session_id,
        intent=None,
        intent_confidence=None,
        has_url=False,
        extracted_urls=[],
        jd_text=None,
        jd_extraction_success=False,
        enhanced_query=None,
        retrieved_assessments=[],
        final_recommendations=[],
        general_answer=None,
        error_message=None,
        processing_steps=[],
        agent_outputs={}
    )