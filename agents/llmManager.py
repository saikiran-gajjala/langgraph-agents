from langchain_core.prompts import ChatPromptTemplate
from agents.logger import setup_logger
from langchain_groq import ChatGroq
import os

logger = setup_logger(__name__)

class LLMManager:
    def __init__(self):
        try:
            logger.info("Initializing LLMManager")
            self.llm = ChatGroq(
                model="llama-3.1-70b-versatile",
                temperature=0.0,
                max_retries=2,
            )
            logger.info("LLMManager initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing LLMManager: {e}")
            raise

    def invoke(self, prompt: ChatPromptTemplate, **kwargs) -> str:
        try:
            logger.info(f"Invoking LLM with prompt: {prompt}")
            messages = prompt.format_messages(**kwargs)
            response = self.llm.invoke(messages)
            logger.info(f"LLM response: {response.content}")
            return response.content
        except Exception as e:
            logger.error(f"Error invoking LLM: {e}")
            raise
