from typing import List, Dict, Any, Optional
from datetime import datetime
from app.database.chroma_db import get_chroma_client
from app.services.embedding_service import get_embedding_service
from app.models.assessment import Assessment
from app.config import settings
from app.utils.logger import get_logger
from app.utils.helpers import chunk_list

logger = get_logger("vector_store_service")


class VectorStoreService:
    """
    Vector store service for indexing and searching assessments
    """
    
    def __init__(self):
        self.chroma_manager = get_chroma_client()
        self.embedding_service = get_embedding_service()
        self.similarity_threshold = settings.RAG_SIMILARITY_THRESHOLD
        
        logger.info(
            f"VectorStoreService initialized - "
            f"Threshold: {self.similarity_threshold:.2f}, "
            f"Embedding dimension: 3072 (text-embedding-3-large)"
        )
    
    async def index_assessments(
        self,
        assessments: Dict[str, Dict[str, Any]],
        batch_size: int = 20
    ) -> int:
        """
        Index assessments into vector store
        
        Args:
            assessments: Dictionary of assessments (url -> data)
            batch_size: Batch size for embedding generation
            
        Returns:
            Number of assessments indexed
        """
        try:
            logger.info(f"Starting to index {len(assessments)} assessments")
            assessment_objects = []
            for url, data in assessments.items():
                try:
                    assessment = Assessment(**data)
                    assessment_objects.append(assessment)
                except Exception as e:
                    logger.warning(f"Failed to parse assessment {url}: {e}")
                    continue
            
            if not assessment_objects:
                logger.warning("No valid assessments to index")
                return 0
            
            documents = []
            metadatas = []
            ids = []
            
            for assessment in assessment_objects:
                doc_text = assessment.to_embedding_text()
                documents.append(doc_text)
                metadata = {
                    "name": assessment.name,
                    "url": assessment.url,
                    "test_type": ",".join(assessment.test_type),
                    "remote_support": assessment.remote_support,
                    "adaptive_support": assessment.adaptive_support,
                    "duration": assessment.duration or -1,
                    "job_levels": assessment.job_levels,
                    "languages": assessment.languages,
                    "description": assessment.description
                }
                metadatas.append(metadata)
                
                doc_id = assessment.url.replace("https://", "").replace("http://", "").replace("/", "_")
                ids.append(doc_id)
            
            logger.info(f"Generating embeddings for {len(documents)} documents")
            embeddings = await self.embedding_service.generate_embeddings(
                documents,
                batch_size=batch_size
            )

            batch_size = 100 
            doc_batches = chunk_list(documents, batch_size)
            emb_batches = chunk_list(embeddings, batch_size)
            meta_batches = chunk_list(metadatas, batch_size)
            id_batches = chunk_list(ids, batch_size)
            
            for i, (docs, embs, metas, batch_ids) in enumerate(
                zip(doc_batches, emb_batches, meta_batches, id_batches)
            ):
                logger.info(f"Indexing batch {i + 1}/{len(doc_batches)}")
                self.chroma_manager.add_documents(
                    documents=docs,
                    embeddings=embs,
                    metadatas=metas,
                    ids=batch_ids
                )
            
            logger.info(f"Successfully indexed {len(assessment_objects)} assessments")
            return len(assessment_objects)
            
        except Exception as e:
            logger.error(f"Failed to index assessments: {e}")
            raise
    
    async def search_assessments(
        self,
        query: str,
        top_k: int = 15,
        filters: Optional[Dict[str, Any]] = None,
        min_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant assessments with CORRECT similarity scoring
        
        Args:
            query: Search query
            top_k: Number of results to return
            filters: Optional metadata filters
            min_score: Optional minimum similarity score
            
        Returns:
            List of matching assessments with correct similarity scores
        """
        try:
            query_embedding = await self.embedding_service.generate_query_embedding(query)
            results = self.chroma_manager.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filters
            )
            
            assessments = []
            
            if results and results['ids'] and len(results['ids']) > 0:
                for i in range(len(results['ids'][0])):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i]
                    similarity_score = 1.0 - (distance / 2.0)
                    
                    similarity_score = max(0.0, min(1.0, similarity_score))
                    
                    test_types = metadata.get('test_type', '').split(',')
                    test_types = [t.strip() for t in test_types if t.strip()]
                    
                    assessment_data = {
                        "name": metadata.get('name', ''),
                        "url": metadata.get('url', ''),
                        "test_type": test_types,
                        "remote_support": metadata.get('remote_support', 'No'),
                        "adaptive_support": metadata.get('adaptive_support', 'No'),
                        "duration": metadata.get('duration', -1),
                        "job_levels": metadata.get('job_levels', ''),
                        "languages": metadata.get('languages', ''),
                        "description": metadata.get('description', ''),
                        "similarity_score": similarity_score,
                        "cosine_distance": distance
                    }
                    
                    if assessment_data['duration'] == -1:
                        assessment_data['duration'] = None
                    
                    assessments.append(assessment_data)
            
            if assessments:
                scores = [a['similarity_score'] for a in assessments]
                distances = [a['cosine_distance'] for a in assessments]
                
                logger.info(
                    f"Retrieved {len(assessments)} assessments - "
                    f"Similarities: [{min(scores):.3f} - {max(scores):.3f}] "
                    f"avg={sum(scores)/len(scores):.3f} | "
                    f"Distances: [{min(distances):.3f} - {max(distances):.3f}]"
                )
                
                # Log score distribution
                score_ranges = {
                    '0.90+': sum(1 for s in scores if s >= 0.90),
                    '0.80-0.90': sum(1 for s in scores if 0.80 <= s < 0.90),
                    '0.70-0.80': sum(1 for s in scores if 0.70 <= s < 0.80),
                    '0.60-0.70': sum(1 for s in scores if 0.60 <= s < 0.70),
                    '0.50-0.60': sum(1 for s in scores if 0.50 <= s < 0.60),
                    '<0.50': sum(1 for s in scores if s < 0.50)
                }
                
                logger.info(f"Score distribution: {score_ranges}")
            
            # Apply score filtering if specified
            if min_score is not None:
                filtered = [a for a in assessments if a['similarity_score'] >= min_score]
                logger.info(
                    f"Score filter ({min_score:.2f}): "
                    f"{len(filtered)}/{len(assessments)} passed"
                )
                return filtered
            
            return assessments
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def search_with_threshold(
        self,
        query: str,
        threshold: float,
        top_k: int = 20,
        fallback_threshold: Optional[float] = None,
        min_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search with automatic threshold fallback
        
        Args:
            query: Search query
            threshold: Primary similarity threshold
            top_k: Initial retrieval count
            fallback_threshold: Fallback threshold if too few results
            min_results: Minimum number of results to aim for
            
        Returns:
            List of assessments meeting threshold
        """
        all_results = await self.search_assessments(query=query, top_k=top_k)
        
        if not all_results:
            logger.warning("No results from vector search")
            return []
        
        filtered = [a for a in all_results if a['similarity_score'] >= threshold]
        
        logger.info(
            f"Primary threshold ({threshold:.2f}): "
            f"{len(filtered)}/{len(all_results)} results"
        )
        
        if len(filtered) >= min_results:
            return filtered
        
        if fallback_threshold is not None and fallback_threshold < threshold:
            filtered_fallback = [
                a for a in all_results 
                if a['similarity_score'] >= fallback_threshold
            ]
            
            logger.info(
                f"Fallback threshold ({fallback_threshold:.2f}): "
                f"{len(filtered_fallback)}/{len(all_results)} results"
            )
            
            if len(filtered_fallback) >= min_results:
                return filtered_fallback
        
        logger.warning(
            f"Could not meet minimum results ({min_results}) even with fallback. "
            f"Returning all {len(all_results)} results sorted by score"
        )
        
        return sorted(all_results, key=lambda x: x['similarity_score'], reverse=True)
    
    async def get_assessment_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get specific assessment by URL
        
        Args:
            url: Assessment URL
            
        Returns:
            Assessment data or None
        """
        try:
            doc_id = url.replace("https://", "").replace("http://", "").replace("/", "_")
            results = self.chroma_manager.get_by_ids([doc_id])
            
            if results and results['ids']:
                metadata = results['metadatas'][0]
                test_types = metadata.get('test_type', '').split(',')
                test_types = [t.strip() for t in test_types if t.strip()]
                
                return {
                    "name": metadata.get('name', ''),
                    "url": metadata.get('url', ''),
                    "test_type": test_types,
                    "remote_support": metadata.get('remote_support', 'No'),
                    "adaptive_support": metadata.get('adaptive_support', 'No'),
                    "duration": metadata.get('duration') if metadata.get('duration') != -1 else None,
                    "job_levels": metadata.get('job_levels', ''),
                    "languages": metadata.get('languages', ''),
                    "description": metadata.get('description', ''),
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get assessment by URL: {e}")
            return None
    
    async def filter_by_test_type(
        self,
        test_types: List[str],
        top_k: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get assessments filtered by test type
        
        Args:
            test_types: List of test types to filter by
            top_k: Maximum number of results
            
        Returns:
            List of matching assessments
        """
        try:
            query = f"Assessments for {', '.join(test_types)}"
            assessments = await self.search_assessments(
                query=query,
                top_k=top_k
            )
            filtered = []
            for assessment in assessments:
                assessment_types = [t.lower() for t in assessment.get('test_type', [])]
                if any(req_type.lower() in ' '.join(assessment_types) for req_type in test_types):
                    filtered.append(assessment)
            
            return filtered
            
        except Exception as e:
            logger.error(f"Failed to filter by test type: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store
        
        Returns:
            Statistics dictionary
        """
        try:
            count = self.chroma_manager.count_documents()
            
            return {
                "total_assessments": count,
                "collection_name": self.chroma_manager.collection_name,
                "similarity_threshold": self.similarity_threshold,
                "embedding_model": "text-embedding-3-large",
                "embedding_dimension": 3072,
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {}
    
    async def clear_collection(self):
        """Clear all documents from the collection"""
        try:
            self.chroma_manager.recreate_collection()
            logger.info("Collection cleared")
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            raise


vector_store_service = VectorStoreService()


def get_vector_store_service() -> VectorStoreService:
    """Get vector store service instance"""
    return vector_store_service