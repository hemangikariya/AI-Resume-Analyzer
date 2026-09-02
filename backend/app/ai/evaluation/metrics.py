from typing import List, Set
from app.core.logger import logger

def calculate_set_overlap_metrics(predicted: Set[str], ground_truth: Set[str]) -> dict:
    """
    Computes precision, recall, and F1-score between predicted entities/skills
    and standard ground truth sets.
    """
    if not predicted or not ground_truth:
        return {"precision": 0.0, "recall": 0.0, "f1_score": 0.0}
        
    intersection = predicted.intersection(ground_truth)
    intersection_len = len(intersection)
    
    precision = intersection_len / len(predicted)
    recall = intersection_len / len(ground_truth)
    
    if precision + recall > 0:
        f1_score = 2 * (precision * recall) / (precision + recall)
    else:
        f1_score = 0.0
        
    return {
        "precision": round(precision, 2),
        "recall": round(recall, 2),
        "f1_score": round(f1_score, 2)
    }

def calculate_jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """Calculates Jaccard Similarity between two sets of text tokens."""
    if not set_a or not set_b:
        return 0.0
    union = set_a.union(set_b)
    intersection = set_a.intersection(set_b)
    return round(len(intersection) / len(union), 2)
