import uuid
import time
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.schemas import RecommendRequest, RecommendResponse
from app.graph.workflow import execute_query
from app.database.sqlite_db import get_db
from app.services.session_service import get_session_service
from app.utils.logger import get_logger
from app.utils.validators import validate_query_length
from app.utils.formatters import format_assessment_response

logger = get_logger("recommend_route")

router = APIRouter(tags=["recommendations"])


@router.post("/recommend", response_model=RecommendResponse)
async def recommend_assessments(
    request: RecommendRequest,
    db: Session = Depends(get_db)
):
    """
    Main recommendation endpoint
    
    Accepts a job description or natural language query and returns
    recommended assessments.
    
    Args:
        request: Recommendation request with query
        db: Database session
        
    Returns:
        Recommended assessments
    """
    start_time = time.time()
    session_service = get_session_service()
    is_valid, error_msg = validate_query_length(request.query)
    if not is_valid:
        logger.warning(f"Invalid query: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    session_id = str(uuid.uuid4())
    
    logger.info(f"Processing recommendation request for session {session_id}")
    
    try:
        final_state = await execute_query(request.query, session_id)
        recommendations = final_state.get('final_recommendations', [])
        error_message = final_state.get('error_message')
        if error_message:
            logger.warning(f"Workflow completed with error: {error_message}")
        if not recommendations:
            general_answer = final_state.get('general_answer')
            if general_answer:
                logger.info("Query was classified as general, no recommendations")
                raise HTTPException(
                    status_code=400,
                    detail="This appears to be a general question. Please provide a job description or url containing a job description to get recommendations. Or try to use Chainlit frontend for any type of query."
                )
            else:
                logger.warning("No recommendations found")
                raise HTTPException(
                    status_code=404,
                    detail="No matching assessments found for your query. Please try rephrasing or providing more details."
                )
        
        formatted_recommendations = format_assessment_response(recommendations)
        if len(formatted_recommendations) > 10:
            formatted_recommendations = formatted_recommendations[:10]
        
        processing_time = time.time() - start_time
        try:
            interaction_id = session_service.save_interaction(
                session_id=session_id,
                query=request.query,
                query_type='jd_query',
                intent=final_state.get('intent'),
                recommended_assessments=formatted_recommendations,
                processing_time=processing_time,
                error_message=error_message,
                agent_outputs=final_state.get('agent_outputs', {})
            )
            logger.info(f"Saved interaction {interaction_id} for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to save interaction: {e}")
        
        logger.info(
            f"Recommendation completed in {processing_time:.2f}s - "
            f"returned {len(formatted_recommendations)} assessments"
        )
        
        return RecommendResponse(recommended_assessments=formatted_recommendations)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recommendation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )