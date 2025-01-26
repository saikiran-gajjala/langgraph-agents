from agents.logger import setup_logger
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
import os
import getpass

logger = setup_logger(__name__)
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")
# _set_if_undefined("GROQ_API_KEY")

class LLMManager:
    def __init__(self):
        try:
            logger.info("Initializing LLMManager")
            # self.llm = ChatGroq(
            #     model=os.getenv("GROQ_MODEL"),
            #     temperature=0.0,
            #     max_retries=2,
            #     streaming=True,
            #     verbose=True,
            # )
            self.llm = ChatOpenAI(
                    temperature=0,
                    model="gpt-4o",
                    max_tokens=None,
                    timeout=None,
                    max_retries=2,
                )
            self.slm = ChatOpenAI(
                    temperature=0,
                    model="gpt-4o-mini",
                    max_tokens=None,
                    timeout=None,
                    max_retries=2,
                )
            logger.info("LLMManager initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing LLMManager: {e}")
            raise