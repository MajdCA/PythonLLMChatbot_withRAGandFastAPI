import logging
logger = logging.getLogger("geoatlas.prompt")

class PromptBuilder:
    """Handles system prompt and context construction"""
    
    SYSTEM_PROMPT = """You are Geoatlas, a geotechnical monitoring web assistant.
Use the provided knowledge base context to answer accurately. If context doesn't cover the question, use your general knowledge.
Keep responses concise, accurate, and user-friendly. Focus on website navigation and geotechnical monitoring.
If the question is not related to the website or geotechnical monitoring, politely redirect the user."""
    
    @staticmethod
    def get_system_prompt():
        """Return the system prompt"""
        return PromptBuilder.SYSTEM_PROMPT
    
    @staticmethod
    def build_context(context: str) -> str:
        """Build knowledge base context"""
        ctx = context if context else "No specific knowledge found. Use general knowledge."
        logger.debug(f"Context length: {len(ctx)}")
        return ctx
    
    @staticmethod
    def build_full_prompt(query: str, context: str) -> str:
        """Combine system prompt, context, and query into full prompt"""
        system_prompt = PromptBuilder.get_system_prompt()
        kb_context = PromptBuilder.build_context(context)
        prompt = f"{system_prompt}\n\nKNOWLEDGE BASE CONTEXT:\n{kb_context}\n\nUser: {query}\nAssistant:"
        logger.info(f"Built prompt | query_len={len(query)} | context_len={len(kb_context)} | prompt_len={len(prompt)}")
        logger.debug(f"Prompt content:\n{prompt}")
        return prompt
