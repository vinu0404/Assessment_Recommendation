from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.prompts.jd_extraction_prompts import (
    JD_PROCESSOR_SYSTEM_INSTRUCTION,
    get_jd_enhancement_prompt,
    get_query_enhancement_prompt
)
from app.models.schemas import EnhancedQuery
from app.config import settings
from app.utils.helpers import extract_duration_from_text


class JDProcessorAgent(BaseAgent):
    """
    Agent that processes and enhances job descriptions
    """
    
    def __init__(self):
        super().__init__("jd_processor")
        self.enable_query_expansion = settings.ENABLE_QUERY_EXPANSION
        
        self.logger.info(
            f"JD Processor initialized - Query Expansion: {self.enable_query_expansion}"
        )
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process job description using LLM 
        
        handles:
        - Skill extraction with ecosystem understanding
        - Test type inference from requirements
        - Query expansion with related terms
        - Job level determination
        
        Args:
            state: Graph state with 'query' or 'jd_text' field
            
        Returns:
            Updated state with 'enhanced_query' field
        """
        jd_text = state.get('jd_text') or state.get('query', '')
        
        if not jd_text:
            self.logger.warning("No text to process")
            return self.update_state(state, {
                'error_message': 'No text to process'
            })
        
        self.log_input({'text_length': len(jd_text)})
        
        try:
            prompt = get_jd_enhancement_prompt(jd_text)
            
            enhanced = await self.llm_service.generate_structured_output(
                prompt=prompt,
                schema=EnhancedQuery,
                system_instruction=JD_PROCESSOR_SYSTEM_INSTRUCTION
            )
            
            self.logger.info(
                f"LLM extraction: {len(enhanced.extracted_skills)} skills, "
                f"{len(enhanced.required_test_types)} test types, "
                f"{len(enhanced.key_requirements)} requirements"
            )
            
            if self.enable_query_expansion and enhanced.extracted_skills:
                expanded_query = await self._expand_query_with_llm(
                    enhanced.cleaned_query
                )
                self.logger.info(
                    f"Query expansion: {len(enhanced.cleaned_query)} → {len(expanded_query)} chars"
                )
            else:
                expanded_query = enhanced.cleaned_query
            
            final_enhanced = EnhancedQuery(
                original_query=enhanced.original_query,
                cleaned_query=expanded_query,
                extracted_skills=enhanced.extracted_skills,
                extracted_duration=enhanced.extracted_duration,
                extracted_job_levels=enhanced.extracted_job_levels,
                required_test_types=enhanced.required_test_types,
                key_requirements=enhanced.key_requirements
            )
            
            self.log_output({
                'skills_count': len(final_enhanced.extracted_skills),
                'test_types': final_enhanced.required_test_types,
                'duration': final_enhanced.extracted_duration,
                'query_length': len(final_enhanced.cleaned_query)
            })
            
            return self.update_state(state, {
                'enhanced_query': final_enhanced
            })
            
        except Exception as e:
            self.logger.error(f"JD processing failed: {e}")
            fallback_enhanced = EnhancedQuery(
                original_query=jd_text,
                cleaned_query=jd_text,
                extracted_skills=[],
                extracted_duration=extract_duration_from_text(jd_text),
                extracted_job_levels=["Mid-Professional"], 
                required_test_types=["K", "P"],  
                key_requirements=[]
            )
            
            return self.update_state(state, {
                'enhanced_query': fallback_enhanced,
                'error_message': f"JD processing error (using fallback): {str(e)}"
            })
    
    async def _expand_query_with_llm(self, original_query: str) -> str:
        """
        Expand query using LLM
        
        Args:
            original_query: The base query to expand
            
        Returns:
            Expanded query with related terms and context
        """
        try:
            prompt = get_query_enhancement_prompt(original_query)
            
            response = await self.llm_service.generate_text(
                prompt=prompt,
                system_instruction=JD_PROCESSOR_SYSTEM_INSTRUCTION
            )
            expanded_query = response.strip()
            
            self.logger.info(f"LLM query expansion successful")
            
            return expanded_query
            
        except Exception as e:
            self.logger.warning(f"Query expansion failed, using original: {e}")
            return original_query


jd_processor_agent = JDProcessorAgent()


def get_jd_processor_agent() -> JDProcessorAgent:
    """Get JD processor agent instance"""
    return jd_processor_agent