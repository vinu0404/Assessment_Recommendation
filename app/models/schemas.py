from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class RecommendRequest(BaseModel):
    """Request schema for recommendation endpoint"""
    query: str = Field(..., min_length=15, max_length=10000, description="Job description or natural language query")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


# Response Schemas
class AssessmentResponse(BaseModel):
    """Single assessment response"""
    url: str
    name :str
    adaptive_support: str
    description: str
    duration: Optional[int]
    remote_support: str
    test_type: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.shl.com/products/product-catalog/view/python-new/",
                "name": "Python Programming Test",
                "adaptive_support": "No",
                "description": "Multi-choice test that measures the knowledge of Python programming...",
                "duration": 11,
                "remote_support": "Yes",
                "test_type": ["Knowledge & Skills"]
            }
        }


class RecommendResponse(BaseModel):
    """Response schema for recommendation endpoint"""
    recommended_assessments: List[AssessmentResponse]
    
    class Config:
        json_schema_extra = {
            "example": {
                "recommended_assessments": [
                    {
                        "url": "https://www.shl.com/products/product-catalog/view/python-new/",
                        "name": "Python Programming Test",
                        "adaptive_support": "No",
                        "description": "Multi-choice test that measures the knowledge of Python programming...",
                        "duration": 11,
                        "remote_support": "Yes",
                        "test_type": ["Knowledge & Skills"]
                    }
                ]
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy")



# Internal Schemas
class IntentClassification(BaseModel):
    """Intent classification result"""
    intent: str = Field(..., description="Classified intent: jd_query, general, or out_of_context")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    reasoning: Optional[str] = Field(None, description="Reasoning for classification")


class URLExtractionResult(BaseModel):
    """URL extraction result"""
    has_url: bool
    urls: List[str] = Field(default_factory=list)
    primary_url: Optional[str] = None


class JDExtractionResult(BaseModel):
    """Job description extraction result"""
    success: bool
    jd_text: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class EnhancedQuery(BaseModel):
    """Enhanced query with extracted information"""
    original_query: str
    cleaned_query: str
    extracted_skills: List[str] = Field(default_factory=list)
    extracted_duration: Optional[int] = None
    extracted_job_levels: List[str] = Field(default_factory=list)
    required_test_types: List[str] = Field(default_factory=list)
    key_requirements: List[str] = Field(default_factory=list)


class RAGResult(BaseModel):
    """RAG retrieval result"""
    assessments: List[Dict[str, Any]]
    retrieval_metadata: Dict[str, Any] = Field(default_factory=dict)
    test_type_distribution: Dict[str, int] = Field(default_factory=dict)


class GeneralQueryResult(BaseModel):
    """General query answer result"""
    answer: str
    relevant_assessments: Optional[List[Dict[str, Any]]] = None
    sources: List[str] = Field(default_factory=list)


# Graph State Schema
class GraphState(BaseModel):
    """LangGraph state for workflow"""
    query: str
    session_id: str
    intent: Optional[str] = None
    intent_confidence: Optional[float] = None
    has_url: bool = False
    extracted_urls: List[str] = Field(default_factory=list)
    jd_text: Optional[str] = None
    jd_extraction_success: bool = False
    enhanced_query: Optional[EnhancedQuery] = None
    retrieved_assessments: List[Dict[str, Any]] = Field(default_factory=list)
    final_recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    general_answer: Optional[str] = None
    error_message: Optional[str] = None
    processing_steps: List[str] = Field(default_factory=list)
    agent_outputs: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True





