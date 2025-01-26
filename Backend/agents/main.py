from workflowManager import WorkflowManager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from models.models import Query, QueryResponse
from langchain.globals import set_debug, set_verbose
from llmManager import LLMManager
from agents.logger import setup_logger
import os

logger = setup_logger(__name__)

if os.getenv("ENABLE_DEBUGGING") == "true":
    set_debug(True)
else:
    set_verbose(True)

try:
    logger.info("Initializing managers")
    llm_manager = LLMManager()
    workflow_manager = WorkflowManager(
        llm_manager=llm_manager)
    logger.info("Managers initialized successfully")
except Exception as e:
    logger.error(f"Error initializing managers: {e}")
    raise

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def redirect_root_to_docs():
    """
    Asynchronously redirects the root URL to the documentation page.

    Returns:
        RedirectResponse: A response object that redirects to the "/docs" URL.
    """
    return RedirectResponse("/docs")


@app.post("/query")
async def runQuery(query: Query) -> QueryResponse:
    """
    Asynchronously processes a query and returns a response.

    Args:
        query (Query): The query object containing the query string.

    Returns:
        QueryResponse: The response object containing the answer and chart.

    Raises:
        HTTPException: If an error occurs while processing the query, an HTTP 500 error is raised with the error details.
    """
    try:
        logger.info(f"Processing query: {query.query}")
        finalResponse = QueryResponse(answer='', chart='')
        finalResponse = workflow_manager.invoke(query.query)
        logger.info(f"Query processed successfully: {finalResponse.answer}")
        return finalResponse
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    try:
        logger.info("Starting the GenAI Langgraph application")
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8001)
    except Exception as e:
        logger.error(f"Error starting the application: {e}")
        raise
