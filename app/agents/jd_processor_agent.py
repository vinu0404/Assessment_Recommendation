from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.prompts.jd_extraction_prompts import (
    JD_PROCESSOR_SYSTEM_INSTRUCTION,
    get_jd_enhancement_prompt
)
from app.models.schemas import EnhancedQuery
from app.config import settings
from app.utils.helpers import extract_duration_from_text
from app.utils.assessment_map import get_assessment_map, get_fallback_skill


class JDProcessorAgent(BaseAgent):
    """
    Agent that processes and enhances job descriptions with improved search query building
    """
    
    def __init__(self):
        super().__init__("jd_processor")
        self.enable_query_expansion = settings.ENABLE_QUERY_EXPANSION
        
        self.logger.info(
            f"JD Processor initialized - Query Expansion: {self.enable_query_expansion}"
        )
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process job description and create optimized search query
        
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
            search_query = self._build_optimized_search_query(enhanced, jd_text)
            
            self.logger.info(f"Search query built: {len(search_query)} chars")
            final_enhanced = EnhancedQuery(
                original_query=enhanced.original_query,
                cleaned_query=search_query,
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
                cleaned_query=self._create_fallback_query(jd_text),
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
    
    def _build_optimized_search_query(self, enhanced: EnhancedQuery, original_text: str) -> str:
        """
        Build search query optimized for vector retrieval
        
        Strategy:
        1. Include specific assessment-related terms
        2. Map skills to likely assessment names
        3. Include job level and test type context
        """
        query_parts = []

        assessment_mappings = get_assessment_map()
        text_lower = original_text.lower()
        for keyword, assessment_terms in assessment_mappings.items():
            if keyword in text_lower:
                query_parts.append(assessment_terms)
        if enhanced.extracted_skills:
            top_skills = enhanced.extracted_skills[:6]
            skills_text = ' '.join(top_skills)
            query_parts.append(f"{skills_text} assessment test evaluation")
        
        if enhanced.extracted_job_levels:
            level_terms = {
                'Entry': 'entry-level graduate foundational basic',
                'Mid': 'intermediate professional',
                'Senior': 'senior advanced experienced',
                'Manager': 'manager management leadership',
                'Executive': 'executive leadership strategic'
            }
            for level in enhanced.extracted_job_levels:
                if level in level_terms:
                    query_parts.append(level_terms[level])
        
        test_type_terms = {
            'K': 'knowledge skills proficiency',
            'P': 'personality behavior work style',
            'A': 'aptitude reasoning ability',
            'C': 'competencies leadership management',
            'B': 'situational judgment decision-making',
            'S': 'simulation exercise practical'
        }
        
        for test_type in enhanced.required_test_types[:3]: 
            if test_type in test_type_terms:
                query_parts.append(test_type_terms[test_type])
        
        if enhanced.key_requirements:
            top_reqs = ' '.join(enhanced.key_requirements[:3])
            query_parts.append(top_reqs)
        
        search_query = ' '.join(query_parts)
        if len(search_query) > 500:
            search_query = search_query[:500]
        
        return search_query
    
    def _create_fallback_query(self, text: str) -> str:
        """Create basic fallback query when LLM extraction fails"""
        keywords = []
        
        skill_keywords = get_fallback_skill()
        text_lower = text.lower()
        for keyword in skill_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        if not keywords:
            return text[:200]
        
        return ' '.join(keywords) + ' assessment test evaluation'


jd_processor_agent = JDProcessorAgent()
def get_jd_processor_agent() -> JDProcessorAgent:
    """Get JD processor agent instance"""
    return jd_processor_agent