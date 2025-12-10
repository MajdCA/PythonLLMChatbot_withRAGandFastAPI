import logging
logger = logging.getLogger("geoatlas.prompt")

class PromptBuilder:
    """Handles system prompt and context construction"""
    
    SYSTEM_PROMPT = """You are Geoatlas, a helpful geotechnical monitoring assistant.

CRITICAL RULES:
1. Answer in EXACTLY 2-3 sentences
2. Use ONLY the context provided below
3. Be consistent - same question = same answer
4. No elaboration beyond what's asked

Answer briefly using the context provided.
If the context doesn't contain the answer, say "I don't have that information."""
    
    @staticmethod
    def get_system_prompt():
        """Return the system prompt"""
        logger.debug(f"System prompt length: {len(PromptBuilder.SYSTEM_PROMPT)}")
        return PromptBuilder.SYSTEM_PROMPT
    
    @staticmethod
    def build_full_prompt(query: str, context: str = "") -> str:
        """Build simple prompt: Context + Question format"""
        logger.info("="*80)
        logger.info("BUILDING PROMPT")
        logger.info("="*80)
        
        system_prompt = PromptBuilder.get_system_prompt()
        
        # Simple template: System -> Context -> Question
        if context and context.strip():
            prompt = f"""{system_prompt}

Context:
{context}

Question: {query}
Answer:"""
        else:
            prompt = f"""{system_prompt}

Question: {query}
Answer:"""
        
        logger.info(f"Prompt stats | query_len={len(query)} | context_len={len(context)} | total_len={len(prompt)}")
        logger.debug("="*80)
        logger.debug("FULL PROMPT SENT TO LLM:")
        logger.debug("="*80)
        logger.debug(f"\n{prompt}\n")
        logger.debug("="*80)
        
        return prompt
