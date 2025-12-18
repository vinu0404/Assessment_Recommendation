"""
SHL Assessment Recommendation System - Evaluation Script

This script evaluates the recommendation system using:
1. Recall@K metric on labeled training data
2. Generates predictions for test set
3. Saves incorrect predictions for prompt fine-tuning
"""

import json
import requests
import time
from typing import List, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime
import csv

API_BASE_URL = "http://localhost:8000"
RECOMMEND_ENDPOINT = f"{API_BASE_URL}/recommend"
TRAIN_DATA_PATH = "./data/labeled_train_set.json"
RESULTS_DIR = "./evaluation_results"

K_VALUES = [1, 3, 5, 8, 10] 
REQUEST_DELAY = 1.0  


class EvaluationMetrics:
    """Calculate evaluation metrics"""
    
    @staticmethod
    def recall_at_k(predicted_urls: List[str], ground_truth_url: str, k: int) -> float:
        """
        Calculate Recall@K
        
        Args:
            predicted_urls: List of predicted assessment URLs
            ground_truth_url: Ground truth URL
            k: Top K predictions to consider
            
        Returns:
            Recall score (0.0 or 1.0 for single ground truth)
        """
        if not predicted_urls or not ground_truth_url:
            return 0.0
        
        predicted_normalized = [url.rstrip('/').lower() for url in predicted_urls[:k]]
        ground_truth_normalized = ground_truth_url.rstrip('/').lower()
        return 1.0 if ground_truth_normalized in predicted_normalized else 0.0
    
    @staticmethod
    def mean_recall_at_k(recalls: List[float]) -> float:
        """Calculate mean recall across all queries"""
        if not recalls:
            return 0.0
        return sum(recalls) / len(recalls)


class RecommendationEvaluator:
    """Main evaluation class"""
    
    def __init__(self):
        self.results_dir = Path(RESULTS_DIR)
        self.results_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.train_results = []
        self.test_predictions = []
        self.incorrect_predictions = []
        
        print(f"Evaluation initialized - Results saved to: {self.results_dir}")
    
    def load_data(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Load train and test data"""
        with open(TRAIN_DATA_PATH, 'r', encoding='utf-8') as f:
            train_data = json.load(f)
        print(f" Loaded {len(train_data)} training queries")
        
        return train_data
    
    def call_recommend_api(self, query: str) -> Dict[str, Any]:
        """
        Call the /recommend API endpoint
        
        Args:
            query: Job description or query text
            
        Returns:
            API response dict
        """
        try:
            response = requests.post(
                RECOMMEND_ENDPOINT,
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API returned status {response.status_code}: {response.text}")
                return {"recommended_assessments": []}
        
        except requests.exceptions.RequestException as e:
            print(f" API call failed: {e}")
            return {"recommended_assessments": []}
    
    def evaluate_train_set(self, train_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Evaluate on training set and calculate Recall@K
        
        Args:
            train_data: Dictionary of {query: ground_truth_url}
            
        Returns:
            Evaluation metrics
        """
        print(f"\nEvaluating on training set ({len(train_data)} queries)...")
        
        recalls_by_k = {k: [] for k in K_VALUES}
        query_count = 0
        
        for query, ground_truth_url in train_data.items():
            query_count += 1
            print(f"\n[{query_count}/{len(train_data)}] Processing query...")
            print(f"Query: {query[:100]}...")
            print(f"Ground Truth: {ground_truth_url}")
            
            response = self.call_recommend_api(query)
            time.sleep(REQUEST_DELAY) 
            predicted_assessments = response.get('recommended_assessments', [])
            predicted_urls = [a['url'] for a in predicted_assessments]
            
            print(f"Predictions: {len(predicted_urls)} assessments returned")
            recalls_for_query = {}
            for k in K_VALUES:
                recall = EvaluationMetrics.recall_at_k(predicted_urls, ground_truth_url, k)
                recalls_by_k[k].append(recall)
                recalls_for_query[f"recall@{k}"] = recall
                print(f"  Recall@{k}: {recall:.2f}")
            
            result = {
                "query": query,
                "ground_truth_url": ground_truth_url,
                "predicted_urls": predicted_urls[:10],  
                "predicted_assessments": predicted_assessments[:10],
                **recalls_for_query
            }
            self.train_results.append(result)
            if recalls_for_query["recall@5"] == 0.0:  
                self.incorrect_predictions.append({
                    "query": query,
                    "ground_truth_url": ground_truth_url,
                    "ground_truth_name": self._extract_name_from_url(ground_truth_url),
                    "predicted_assessments": predicted_assessments[:5],
                    "reason": "Ground truth not in top 5 predictions"
                })
                print(" INCORRECT: Ground truth not in top 5")
        
        mean_recalls = {}
        for k in K_VALUES:
            mean_recall = EvaluationMetrics.mean_recall_at_k(recalls_by_k[k])
            mean_recalls[f"mean_recall@{k}"] = mean_recall
        
        print("\n" + "=" * 80)
        print("TRAINING SET EVALUATION RESULTS")
        print("=" * 80)
        for k in K_VALUES:
            print(f"Mean Recall@{k}: {mean_recalls[f'mean_recall@{k}']:.4f}")
        print(f"\nIncorrect Predictions: {len(self.incorrect_predictions)}/{len(train_data)}")
        print("=" * 80)
        
        return mean_recalls
    
    
    def save_results(self, metrics: Dict[str, Any]):
        """Save all evaluation results to files"""
        print("\nSaving results...")
        
        train_results_file = self.results_dir / f"train_evaluation_{self.timestamp}.json"
        with open(train_results_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": self.timestamp,
                "metrics": metrics,
                "total_queries": len(self.train_results),
                "results": self.train_results
            }, f, indent=2, ensure_ascii=False)
        print(f"Training results: {train_results_file}")
        
        incorrect_file = self.results_dir / f"incorrect_predictions_{self.timestamp}.json"
        with open(incorrect_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": self.timestamp,
                "total_incorrect": len(self.incorrect_predictions),
                "incorrect_predictions": self.incorrect_predictions
            }, f, indent=2, ensure_ascii=False)
        print(f"   ✓ Incorrect predictions: {incorrect_file}")


        summary_file = self.results_dir / f"summary_{self.timestamp}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("SHL ASSESSMENT RECOMMENDATION SYSTEM - EVALUATION SUMMARY\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Evaluation Timestamp: {self.timestamp}\n")
            f.write(f"API Endpoint: {RECOMMEND_ENDPOINT}\n\n")
            
            f.write("TRAINING SET METRICS:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Queries: {len(self.train_results)}\n")
            for metric, value in metrics.items():
                f.write(f"{metric}: {value:.4f}\n")
            f.write(f"\nIncorrect Predictions: {len(self.incorrect_predictions)}\n")
            f.write(f"Accuracy@5: {1 - (len(self.incorrect_predictions) / len(self.train_results)):.4f}\n\n")
            
        
        print(f"   ✓ Summary report: {summary_file}")
        print("\n✅ All results saved successfully!")
    
    @staticmethod
    def _extract_name_from_url(url: str) -> str:
        """Extract assessment name from URL"""
        parts = url.rstrip('/').split('/')
        if parts:
            name = parts[-1].replace('-', ' ').title()
            return name
        return "Unknown"
    
    def run_evaluation(self):
        """Main evaluation workflow"""
        print("\n" + "=" * 80)
        print("SHL ASSESSMENT RECOMMENDATION SYSTEM - EVALUATION")
        print("=" * 80)
        
        train_data, test_data = self.load_data()
        metrics = self.evaluate_train_set(train_data)
        self.save_results(metrics)
        
        print("EVALUATION COMPLETE!")
        print(f"\nResults saved in: {self.results_dir}")


def main():
    """Entry point"""
    evaluator = RecommendationEvaluator()
    evaluator.run_evaluation()


if __name__ == "__main__":
    main()