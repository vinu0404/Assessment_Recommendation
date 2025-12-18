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
    RAG Agent with improved retrieval and intelligent reranking
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
        Retrieve and rank assessments with improved matching
        
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
            search_query = enhanced_query.cleaned_query
            
            self.logger.info(f"Vector search query: {search_query[:200]}...")
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
            
            filtered = self._filter_by_similarity_threshold(retrieved)
            self.logger.info(f"After threshold filter: {len(filtered)} assessments")
            
            if self.enable_llm_reranking and len(filtered) > 0:
                reranked = await self._rerank_with_llm(filtered, enhanced_query)
                self.logger.info(f"After LLM reranking: {len(reranked)} assessments")
            else:
                reranked = sorted(
                    filtered,
                    key=lambda x: x.get('similarity_score', 0),
                    reverse=True
                )
            
            final_recommendations = self._select_final_recommendations(
                reranked,
                enhanced_query
            )
            
            self.logger.info(
                f"Final: {len(final_recommendations)} assessments"
            )
            
            stats = self._calculate_statistics(final_recommendations)
            
            self.log_output({
                'final_count': len(final_recommendations),
                'avg_score': stats['avg_score'],
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
    
    def _filter_by_duration(
        self,
        assessments: List[Dict[str, Any]],
        max_duration: int
    ) -> List[Dict[str, Any]]:
        """Filter by duration constraint (strict)"""
        return [
            a for a in assessments 
            if a.get('duration') is None or a.get('duration') <= max_duration
        ]
    
    def _filter_by_similarity_threshold(
        self,
        assessments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter by similarity threshold with fallback"""
        filtered = [
            a for a in assessments 
            if a.get('similarity_score', 0) >= self.similarity_threshold
        ]
        
        if len(filtered) >= self.min_select:
            return filtered
        
        filtered_fallback = [
            a for a in assessments 
            if a.get('similarity_score', 0) >= self.similarity_threshold_fallback
        ]
        
        if len(filtered_fallback) >= self.min_select:
            return filtered_fallback
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
        LLM-based reranking with improved prompt
        """
        if len(assessments) <= self.max_select:
            return assessments
        
        try:
            assessments_text = "\n\n".join([
                f"ID: {i}\n"
                f"Name: {a.get('name', 'Unknown')}\n"
                f"Description: {a.get('description', 'No description')}\n"
                f"Test Types: {', '.join(a.get('test_type', []))}\n"
                f"Duration: {a.get('duration', 'Unknown')} minutes\n"
                f"Job Levels: {a.get('job_levels', 'Not specified')}\n"
                f"Vector Score: {a.get('similarity_score', 0):.3f}"
                for i, a in enumerate(assessments[:20])
            ])
            
            prompt = get_reranking_prompt(
                query=enhanced_query.original_query,
                skills=enhanced_query.extracted_skills,
                test_types=enhanced_query.required_test_types,
                job_levels=enhanced_query.extracted_job_levels,
                duration_constraint=f"{enhanced_query.extracted_duration} minutes" if enhanced_query.extracted_duration else "None",
                assessments=assessments_text,
                top_k=self.max_select
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
                if 0 <= idx < len(assessments):
                    assessment = assessments[idx].copy()
                    assessment['llm_score'] = ranking.get('score', 0.5)
                    assessment['llm_reason'] = ranking.get('reason', '')
                    assessment['combined_score'] = (
                        0.0 * assessment.get('similarity_score', 0) + 
                        1 * assessment['llm_score']
                    )
                    reranked.append(assessment)
            reranked.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
            
            self.logger.info(
                f"LLM reranked {len(reranked)} assessments"
            )
            
            return reranked
            
        except Exception as e:
            self.logger.warning(f"LLM reranking failed: {e}, using vector scores")
            return sorted(
                assessments,
                key=lambda x: x.get('similarity_score', 0),
                reverse=True
            )
    
    def _select_final_recommendations(
        self,
        assessments: List[Dict[str, Any]],
        enhanced_query: EnhancedQuery
    ) -> List[Dict[str, Any]]:
        """
        Select final recommendations ensuring diversity and coverage
        """
        if len(assessments) <= self.min_select:
            return assessments
        
        selected = []
        seen_names = set()
        test_type_counts = Counter()
        for assessment in assessments:
            if len(selected) >= self.max_select:
                break
            
            name = assessment.get('name', '')
            if name in seen_names:
                continue
            test_types = assessment.get('test_type', [])
            max_per_type = 3  
            type_ok = all(test_type_counts[tt] < max_per_type for tt in test_types)
            
            if type_ok or len(selected) < self.min_select:
                selected.append(assessment)
                seen_names.add(name)
                for tt in test_types:
                    test_type_counts[tt] += 1
        
        if len(selected) < self.min_select:
            remaining = [a for a in assessments if a.get('name') not in seen_names]
            selected.extend(remaining[:self.min_select - len(selected)])
        
        selected.sort(
            key=lambda x: x.get('combined_score', x.get('similarity_score', 0)),
            reverse=True
        )
        
        return selected
    
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