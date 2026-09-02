import numpy as np
from typing import List, Dict, Any, Optional
from app.ai.engines.embedding_engine import get_text_embedding
from app.core.logger import logger

class RetrievalService:
    @staticmethod
    def chunk_parsed_resume(parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Splits a parsed resume into section-aware chunks.
        Each chunk is returned as a dict: {"section": section_name, "text": chunk_text}.
        """
        chunks = []
        
        # 1. Contact Chunk
        contact = parsed_data.get("contact", {})
        if contact:
            contact_text = (
                f"Candidate Name: {contact.get('name', 'Unknown')}\n"
                f"Email: {contact.get('email', 'N/A')}\n"
                f"Phone: {contact.get('phone', 'N/A')}\n"
                f"LinkedIn: {contact.get('linkedin', 'N/A')}\n"
                f"GitHub: {contact.get('github', 'N/A')}"
            )
            chunks.append({"section": "contact", "text": contact_text})
            
        # 2. Skills Chunk
        skills = parsed_data.get("skills", [])
        if skills:
            chunks.append({"section": "skills", "text": f"Technical Skills: {', '.join(skills)}"})
            
        # 3. Education Chunk
        education = parsed_data.get("education", [])
        if education:
            edu_lines = []
            for edu in education:
                edu_lines.append(f"- {edu.get('degree', 'Degree')} at {edu.get('institution', 'Institution')} ({edu.get('year', 'N/A')})")
            chunks.append({"section": "education", "text": "Education History:\n" + "\n".join(edu_lines)})
            
        # 4. Experience Chunks
        experience = parsed_data.get("experience", [])
        for exp in experience:
            exp_text = (
                f"Work Experience at {exp.get('company', 'Unknown Company')}:\n"
                f"Role: {exp.get('title', 'Role')}\n"
                f"Duration: {exp.get('duration', 'N/A')}\n"
                f"Description: {exp.get('description', '')}"
            )
            chunks.append({"section": "experience", "text": exp_text})
            
        # 5. Projects Chunks
        projects = parsed_data.get("projects", [])
        for proj in projects:
            proj_text = (
                f"Project: {proj.get('title', 'Project Title')}\n"
                f"Description: {proj.get('description', '')}"
            )
            chunks.append({"section": "projects", "text": proj_text})
            
        # 6. Additional sections
        sections = parsed_data.get("sections", {})
        for sec_name, sec_vals in sections.items():
            if sec_name not in ["skills", "education", "experience", "projects"] and sec_vals:
                if isinstance(sec_vals, list):
                    sec_text = f"{sec_name.capitalize()}: {', '.join(sec_vals)}"
                else:
                    sec_text = f"{sec_name.capitalize()}: {sec_vals}"
                chunks.append({"section": sec_name, "text": sec_text})
                
        return chunks

    @staticmethod
    def retrieve_context(
        parsed_data: Dict[str, Any],
        query: str,
        top_k: int = 3
    ) -> str:
        """
        Builds a vector index of resume chunks, embeds the query,
        retrieves the top-k most relevant chunks using FAISS (or NumPy cosine similarity fallback).
        Falls back to raw resume context if extraction fails.
        """
        logger.info("Initializing RAG context retrieval...")
        chunks = RetrievalService.chunk_parsed_resume(parsed_data)
        if not chunks:
            return ""
            
        try:
            # 1. Compute embeddings for all chunks and normalize
            chunk_embeddings = []
            valid_chunks = []
            
            for chunk in chunks:
                text = chunk["text"]
                if text.strip():
                    emb = get_text_embedding(text)
                    norm = np.linalg.norm(emb)
                    if norm > 0:
                        chunk_embeddings.append(emb / norm)
                        valid_chunks.append(chunk)
                        
            if not chunk_embeddings:
                logger.warning("No valid chunk embeddings generated. Reverting to fallback.")
                return RetrievalService.get_fallback_context(parsed_data)
                
            chunk_embeddings = np.array(chunk_embeddings, dtype=np.float32)
            
            # 2. Embed and normalize the query
            query_emb = get_text_embedding(query)
            query_norm = np.linalg.norm(query_emb)
            if query_norm > 0:
                query_emb = query_emb / query_norm
            else:
                return RetrievalService.get_fallback_context(parsed_data)
                
            k = min(top_k, len(valid_chunks))
            
            # 3. Vector Similarity Search (FAISS if available, else NumPy dot product)
            try:
                import faiss
                dimension = chunk_embeddings.shape[1]
                index = faiss.IndexFlatIP(dimension)
                index.add(chunk_embeddings)
                distances, indices = index.search(np.array([query_emb], dtype=np.float32), k)
                top_indices = [int(indices[0][i]) for i in range(k)]
                top_sims = [float(distances[0][i]) for i in range(k)]
            except (ImportError, Exception) as fe:
                logger.info(f"FAISS unavailable ({fe}). Computing RAG retrieval via NumPy.")
                sims = np.dot(chunk_embeddings, query_emb)
                top_indices = np.argsort(sims)[::-1][:k].tolist()
                top_sims = [float(sims[idx]) for idx in top_indices]
            
            # 4. Format retrieved chunks
            retrieved_texts = []
            for i, idx in enumerate(top_indices):
                if 0 <= idx < len(valid_chunks):
                    chunk = valid_chunks[idx]
                    sim = top_sims[i]
                    logger.info(f"Retrieved chunk from section '{chunk['section']}' (similarity: {sim:.3f})")
                    retrieved_texts.append(f"[{chunk['section'].upper()} CONTEXT]\n{chunk['text']}")
                    
            formatted_context = "\n\n".join(retrieved_texts)
            return formatted_context
            
        except Exception as e:
            logger.error(f"RAG retrieval pipeline failed: {e}. Falling back to default context.")
            return RetrievalService.get_fallback_context(parsed_data)

    @staticmethod
    def get_fallback_context(parsed_data: Dict[str, Any]) -> str:
        """Fallback to compile the entire resume into context if retrieval fails."""
        contact = parsed_data.get("contact", {})
        education = parsed_data.get("education", [])
        experience = parsed_data.get("experience", [])
        projects = parsed_data.get("projects", [])
        sections = parsed_data.get("sections", {})
        
        return (
            f"Candidate Name: {contact.get('name', 'Unknown')}\n"
            f"Email: {contact.get('email', 'N/A')}\n"
            f"Phone: {contact.get('phone', 'N/A')}\n"
            f"LinkedIn: {contact.get('linkedin', 'N/A')}\n"
            f"GitHub: {contact.get('github', 'N/A')}\n\n"
            f"--- EDUCATION ---\n{education}\n\n"
            f"--- EXPERIENCE ---\n{experience}\n\n"
            f"--- PROJECTS ---\n{projects}\n\n"
            f"--- SKILLS & OTHER DETAILS ---\n{sections}\n"
        )
