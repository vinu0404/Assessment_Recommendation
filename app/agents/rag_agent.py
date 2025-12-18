from typing import Dict, Any, List
from collections import Counter
from app.agents.base_agent import BaseAgent
from app.services.vector_store_service import get_vector_store_service
from app.prompts.rag_prompts import (
    RAG_SYSTEM_INSTRUCTION,
    get_reranking_prompt
)
from app.config import settings
from app.models.schemas import EnhancedQuery
from app.utils.formatters import extract_json_from_response


class RAGAgent(BaseAgent):
    """
    RAG Agent with improved retrieval and selection
    """
    
    def __init__(self):
        super().__init__("rag")
        self.vector_store = get_vector_store_service()
        self.top_k_retrieve = settings.RAG_TOP_K
        self.similarity_threshold = settings.RAG_SIMILARITY_THRESHOLD
        self.similarity_threshold_fallback = settings.RAG_SIMILARITY_THRESHOLD_FALLBACK
        self.min_select = settings.RAG_FINAL_SELECT_MIN
        self.max_select = settings.RAG_FINAL_SELECT_MAX
        self.enable_llm_reranking = settings.RAG_ENABLE_LLM_RERANKING
        
        self.logger.info(
            f"RAG Agent initialized - "
            f"Top-K: {self.top_k_retrieve}, "
            f"Threshold: {self.similarity_threshold:.2f}, "
            f"Range: {self.min_select}-{self.max_select}, "
            f"LLM Reranking: {self.enable_llm_reranking}"
        )
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve and rank assessments based on enhanced query
        
        Args:
            state: Graph state with 'enhanced_query' field
            
        Returns:
            Updated state with 'retrieved_assessments' and 'final_recommendations'
        """
        enhanced_query = state.get('enhanced_query')
        
        if not enhanced_query:
            self.logger.error("No enhanced query in state")
            return self.update_state(state, {
                'error_message': 'No enhanced query available for RAG'
            })
        
        self.log_input({
            'skills': enhanced_query.extracted_skills[:10],
            'test_types': enhanced_query.required_test_types,
            'duration': enhanced_query.extracted_duration,
            'job_levels': enhanced_query.extracted_job_levels
        })
        
        try:
            search_query = self._build_search_query(enhanced_query)
            self.logger.info(f"Search query: {search_query[:200]}...")
            print("\n" + "="*80)
            print("ENHANCED QUERY DETAILS")
            print(f"Original query: {enhanced_query.original_query[:100]}")
            print(f"Cleaned query: {enhanced_query.cleaned_query[:200]}")
            print(f"Extracted skills: {enhanced_query.extracted_skills[:10]}")
            print(f"Key requirements: {enhanced_query.key_requirements[:5]}")
            print(f"Final search query: {search_query[:300]}")
            

            retrieved = await self.vector_store.search_assessments(
                query=search_query,
                top_k=self.top_k_retrieve
            )
            
            if not retrieved:
                self.logger.warning("No assessments retrieved from vector search")
                return self.update_state(state, {
                    'retrieved_assessments': [],
                    'final_recommendations': [],
                    'error_message': 'No matching assessments found'
                })
            
            self.logger.info(
                f"Retrieved {len(retrieved)} candidates - "
                f"Scores: [{min(a.get('similarity_score', 0) for a in retrieved):.3f} - "
                f"{max(a.get('similarity_score', 0) for a in retrieved):.3f}]"
            )

            if enhanced_query.extracted_duration:
                retrieved = self._filter_by_duration(
                    retrieved,
                    enhanced_query.extracted_duration
                )
                self.logger.info(f"After duration filter: {len(retrieved)} assessments")
            
            if self.similarity_threshold > 0:
                filtered = self._filter_by_similarity_threshold(retrieved)
                self.logger.info(f"After threshold filter: {len(filtered)} assessments")
            else:
                filtered = retrieved
                self.logger.info(f"No threshold filter - passing all {len(filtered)} to LLM")
            
            if self.enable_llm_reranking and len(filtered) > 0:
                reranked = await self._rerank_with_llm(filtered, enhanced_query)
                self.logger.info(f"After LLM reranking: {len(reranked)} assessments")
            else:
                reranked = sorted(
                    filtered,
                    key=lambda x: x.get('similarity_score', 0),
                    reverse=True
                )

            final_recommendations = self._select_top_k(reranked)
            
            self.logger.info(
                f"Final: {len(final_recommendations)} assessments - "
                f"Scores: [{final_recommendations[0].get('combined_score', final_recommendations[0].get('similarity_score', 0)):.3f} - "
                f"{final_recommendations[-1].get('combined_score', final_recommendations[-1].get('similarity_score', 0)):.3f}]"
            )
            
            stats = self._calculate_statistics(final_recommendations)
            
            self.log_output({
                'final_count': len(final_recommendations),
                'avg_score': stats['avg_score'],
                'min_score': stats['min_score'],
                'max_score': stats['max_score'],
                'test_type_distribution': stats['test_type_distribution']
            })
            
            return self.update_state(state, {
                'retrieved_assessments': retrieved,
                'final_recommendations': final_recommendations
            })
            
        except Exception as e:
            self.logger.error(f"RAG execution failed: {e}")
            return self.update_state(state, {
                'retrieved_assessments': [],
                'final_recommendations': [],
                'error_message': f"RAG error: {str(e)}"
            })
    
    def _build_search_query(self, enhanced_query: EnhancedQuery) -> str:
        """
        Build search query to generate assessment terminology
        """
        parts = []
        
        if enhanced_query.cleaned_query:
            parts.append(enhanced_query.cleaned_query)
        
        if enhanced_query.extracted_skills:
            skills_text = ", ".join(enhanced_query.extracted_skills[:15])
            parts.append(skills_text)
        
        if enhanced_query.extracted_job_levels:
            levels_text = ", ".join(enhanced_query.extracted_job_levels)
            parts.append(f"Level: {levels_text}")
        
        return " | ".join(parts)
    
    def _filter_by_duration(
        self,
        assessments: List[Dict[str, Any]],
        max_duration: int
    ) -> List[Dict[str, Any]]:
        """Filter by duration constraint - HARD constraint"""
        return [
            a for a in assessments 
            if a.get('duration') is None or a.get('duration') <= max_duration
        ]
    
    def _filter_by_similarity_threshold(
        self,
        assessments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter by similarity threshold with fallback logic"""
        filtered = [
            a for a in assessments 
            if a.get('similarity_score', 0) >= self.similarity_threshold
        ]
        
        if len(filtered) >= self.min_select:
            return filtered
        
        self.logger.warning(
            f"Primary threshold yielded only {len(filtered)} results. "
            f"Trying fallback ({self.similarity_threshold_fallback:.2f})"
        )
        
        filtered_fallback = [
            a for a in assessments 
            if a.get('similarity_score', 0) >= self.similarity_threshold_fallback
        ]
        
        if len(filtered_fallback) >= self.min_select:
            return filtered_fallback
        
        self.logger.warning(
            f"Even fallback yielded only {len(filtered_fallback)}. "
            f"Returning top {self.max_select} by score"
        )
        
        return sorted(
            assessments,
            key=lambda x: x.get('similarity_score', 0),
            reverse=True
        )[:self.max_select]
    
    async def _rerank_with_llm(
        self,
        assessments: List[Dict[str, Any]],
        enhanced_query: EnhancedQuery
    ) -> List[Dict[str, Any]]:
        """
        LLM-based reranking - processes ALL candidates with domain reasoning
        """
        if not assessments:
            return []
        
        try:
            assessments_text = "\n\n".join([
                f"ID: {i}\n"
                f"Name: {a.get('name', 'Unknown')}\n"
                f"Description: {a.get('description', 'No description')[:150]}...\n"
                f"Test Types: {', '.join(a.get('test_type', []))}\n"
                f"Duration: {a.get('duration', 'N/A')} min\n"
                f"Vector Score: {a.get('similarity_score', 0):.3f}"
                for i, a in enumerate(assessments)  
            ])
            
            prompt = get_reranking_prompt(
                query=enhanced_query.cleaned_query,
                skills=enhanced_query.extracted_skills[:15],
                test_types=enhanced_query.required_test_types,
                job_levels=enhanced_query.extracted_job_levels,
                duration_constraint=f"{enhanced_query.extracted_duration} min" if enhanced_query.extracted_duration else "None",
                assessments=assessments_text,
                top_k=min(self.max_select, len(assessments))
            )
            
            response = await self.llm_service.generate_text(
                prompt=prompt,
                system_instruction=RAG_SYSTEM_INSTRUCTION
            )
            
            rankings = extract_json_from_response(response)
            if isinstance(rankings, dict):
                rankings = rankings.get('rankings', [])
            
            reranked = []
            for ranking in rankings:
                idx = ranking.get('id')
                if idx is not None and 0 <= idx < len(assessments):
                    assessment = assessments[idx].copy()
                    assessment['llm_score'] = ranking.get('score', 0.5)
                    assessment['llm_reason'] = ranking.get('reason', '')
                    
                    assessment['combined_score'] = (
                        0.1 * assessment.get('similarity_score', 0) +  
                        0.9 * assessment['llm_score']
                    )
                    reranked.append(assessment)
            
            reranked.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
            
            self.logger.info(
                f"LLM reranked {len(reranked)}/{len(assessments)} assessments - "
                f"Top score: {reranked[0].get('combined_score', 0):.3f}"
            )
            
            return reranked
            
        except Exception as e:
            self.logger.error(f"LLM reranking failed: {e}", exc_info=True)
            return sorted(
                assessments,
                key=lambda x: x.get('similarity_score', 0),
                reverse=True
            )
    
    def _select_top_k(
        self,
        assessments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Select top K assessments
        """
        if not assessments:
            return []
        count = min(len(assessments), self.max_select)
        count = max(count, min(self.min_select, len(assessments)))
        
        return assessments[:count]
    
    def _calculate_statistics(
        self,
        assessments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate recommendation statistics"""
        if not assessments:
            return {
                'avg_score': 0.0,
                'min_score': 0.0,
                'max_score': 0.0,
                'test_type_distribution': {}
            }
        
        scores = [
            a.get('combined_score', a.get('similarity_score', 0)) 
            for a in assessments
        ]
        
        counter = Counter()
        for assessment in assessments:
            for test_type in assessment.get('test_type', []):
                counter[test_type] += 1
        
        return {
            'avg_score': sum(scores) / len(scores),
            'min_score': min(scores),
            'max_score': max(scores),
            'test_type_distribution': dict(counter)
        }

rag_agent = RAGAgent()

def get_rag_agent() -> RAGAgent:
    """Get RAG agent instance"""
    return rag_agent