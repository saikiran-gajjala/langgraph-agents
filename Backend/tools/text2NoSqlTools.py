from datetime import date
from langchain.agents import Tool
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field, model_validator
from agents.mongodb_retriever import get_movies
from agents.logger import setup_logger

logger = setup_logger(__name__)

def get_no_context_response(self):
    try:
        logger.info("Generating no context response")
        return "I cannot answer your question as I don't have the context"
    except Exception as e:
        logger.error(f"Error generating no context response: {e}")
        raise


class TimeStamp(BaseModel):
    fromDate: date = Field()
    toDate: date = Field()


class TimeStampInStrings(BaseModel):
    fromDate: str = Field(None, description="From date in YYYY-MM-DD format")
    toDate: str = Field(None, description="To date in YYYY-MM-DD format")

text2NoSqlTools = [
    Tool(
        name="GetMovies",
        func=get_movies,
        description="""
        Gets information about the movies, ratings, plot or story, cast or actors, and genres based on the user input.
        Args:
            query (str): The user input to send. Accepts user input directly without modification.
        Returns:
            list: List of movies with the requested information.
        """
    ),
    # Fallback
    Tool(
        name="NotAbleToParse",
        func=get_no_context_response,
        description="Fallback tool for unrecognized queries or hallucinated responses."
    )
]
