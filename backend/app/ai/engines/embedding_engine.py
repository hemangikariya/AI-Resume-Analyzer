from typing import List, Dict, Any
import numpy as np
from app.core.cache import get_sentence_transformer
from app.core.logger import logger

# Global in-memory cache to save computed embeddings and avoid duplicate encoding overhead
EMBEDDING_CACHE: Dict[str, np.ndarray] = {}

def get_text_embedding(text: str) -> np.ndarray:
    """
    Generates high-dimensional vector embeddings for a given text segment
    using the cached SentenceTransformer model. Reuses cached embeddings if available.
    """
    clean_text = text.strip()
    if not clean_text:
        return np.zeros(384, dtype=np.float32)
        
    if clean_text in EMBEDDING_CACHE:
        return EMBEDDING_CACHE[clean_text]
        
    try:
        model = get_sentence_transformer()
        embedding = model.encode(clean_text, convert_to_numpy=True)
        EMBEDDING_CACHE[clean_text] = embedding
        return embedding
    except Exception as e:
        logger.error(f"Failed to generate text embedding: {e}")
        return np.zeros(384, dtype=np.float32)

def calculate_semantic_similarity(text1: str, text2: str) -> float:
    """
    Computes the cosine similarity between two text segments.
    Returns a score between 0.0 (entirely dissimilar) and 1.0 (identical semantic meaning).
    """
    if not text1.strip() or not text2.strip():
        return 0.0
        
    try:
        emb1 = get_text_embedding(text1)
        emb2 = get_text_embedding(text2)
        
        # Calculate dot product
        dot_product = np.dot(emb1, emb2)
        
        # Calculate norms
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        similarity = dot_product / (norm1 * norm2)
        
        # Clean and clamp value to [0.0, 1.0] range
        similarity = float(np.clip(similarity, 0.0, 1.0))
        return round(similarity, 3)
        
    except Exception as e:
        logger.error(f"Failed to compute semantic similarity: {e}")
        return 0.0

def match_skills_semantically(
    resume_skills: List[str],
    jd_skills: List[str],
    threshold: float = 0.82
) -> Dict[str, Any]:
    """
    Matches job description skills against resume skills semantically.
    Uses FAISS IndexFlatIP if available, with a clean NumPy cosine-similarity fallback.
    """
    if not resume_skills or not jd_skills:
        return {
            "matched_skills": [],
            "missing_skills": list(jd_skills)
        }
        
    try:
        # 1. Compute embeddings for all resume skills and normalize them for cosine similarity
        res_embeddings_list = []
        clean_res_skills = []
        for s in resume_skills:
            if s.strip():
                emb = get_text_embedding(s)
                norm = np.linalg.norm(emb)
                if norm > 0:
                    res_embeddings_list.append(emb / norm)
                    clean_res_skills.append(s)
                    
        if not res_embeddings_list:
            return {
                "matched_skills": [],
                "missing_skills": list(jd_skills)
            }
            
        res_embeddings = np.array(res_embeddings_list, dtype=np.float32) # Shape: (N, D)
        
        # 2. Compute embeddings for all JD skills and normalize them
        jd_embeddings_list = []
        clean_jd_skills = []
        for s in jd_skills:
            if s.strip():
                emb = get_text_embedding(s)
                norm = np.linalg.norm(emb)
                if norm > 0:
                    jd_embeddings_list.append(emb / norm)
                    clean_jd_skills.append(s)
                    
        if not jd_embeddings_list:
            return {
                "matched_skills": [],
                "missing_skills": list(jd_skills)
            }
            
        jd_embeddings = np.array(jd_embeddings_list, dtype=np.float32) # Shape: (M, D)
        
        # 3. Perform Vector Similarity Search (FAISS if available, else NumPy dot product)
        use_faiss = False
        try:
            import faiss
            dimension = res_embeddings.shape[1]
            index = faiss.IndexFlatIP(dimension)
            index.add(res_embeddings)
            distances, indices = index.search(jd_embeddings, 1)
            use_faiss = True
        except (ImportError, Exception) as fe:
            logger.info(f"FAISS unavailable ({fe}). Utilizing NumPy vectorized cosine similarity.")
            # Shape (M, N) matrix product for exact cosine similarities
            sim_matrix = np.dot(jd_embeddings, res_embeddings.T)
            indices = np.argmax(sim_matrix, axis=1).reshape(-1, 1)
            distances = np.max(sim_matrix, axis=1).reshape(-1, 1)

        matched_skills = []
        missing_skills = []
        
        exact_res_skills_lower = set(s.lower() for s in resume_skills)
        
        for i, jd_skill in enumerate(clean_jd_skills):
            if jd_skill.lower() in exact_res_skills_lower:
                matched_skills.append(jd_skill)
                continue
                
            sim = float(distances[i][0])
            idx = int(indices[i][0])
            
            if sim >= threshold and 0 <= idx < len(clean_res_skills):
                engine_name = "FAISS" if use_faiss else "NumPy"
                logger.info(f"Semantic match ({engine_name}): JD '{jd_skill}' matched with Resume '{clean_res_skills[idx]}' (similarity: {sim:.3f})")
                matched_skills.append(jd_skill)
            else:
                missing_skills.append(jd_skill)
                
        return {
            "matched_skills": list(set(matched_skills)),
            "missing_skills": list(set(missing_skills))
        }
    except Exception as e:
        logger.error(f"Semantic skill matching failed: {e}. Falling back to exact substring match.")
        matched_skills = []
        missing_skills = []
        res_set = set(s.lower() for s in resume_skills)
        for s in jd_skills:
            if s.lower() in res_set:
                matched_skills.append(s)
            else:
                missing_skills.append(s)
        return {
            "matched_skills": list(set(matched_skills)),
            "missing_skills": list(set(missing_skills))
        }
