from workflowManager import WorkflowManager
from fastapi import FastAPI, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from models.models import Query, QueryResponse
from langchain.globals import set_debug, set_verbose
from llmManager import LLMManager
from agents.logger import setup_logger
import getpass
import os

logger = setup_logger(__name__)

if os.getenv("ENABLE_DEBUGGING") == "true":
    set_debug(True)
else:
    set_verbose(True)


def _set_if_undefined(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"Please provide your {var}")


_set_if_undefined("GROQ_API_KEY")

# Initialize managers
try:
    logger.info("Initializing managers")
    llm_manager = LLMManager()
    workflow_manager = WorkflowManager(
        llm_manager=llm_manager)
    logger.info("Managers initialized successfully")
except Exception as e:
    logger.error(f"Error initializing managers: {e}")
    raise

# Create workflow with managers
try:
    logger.info("Generating workflow graph")
    graph = workflow_manager.generate_graph()
    logger.info("Workflow graph generated successfully")
except Exception as e:
    logger.error(f"Error generating workflow graph: {e}")
    raise

app = FastAPI()

origins = ["http://localhost:4200", "http://localhost:3005"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


@app.post("/query")
async def runQuery(query: Query) -> QueryResponse:
    try:
        logger.info(f"Processing query: {query.query}")
        response = []
        finalResponse = QueryResponse(answer='', chart='', reviewImage=None)
        config = {"configurable": {"thread_id": "1"}, "recursion_limit": 100}
        input = {"question": query.query}
        # state = graph.get_state(config)
        for stream_data in graph.stream(input, config):
            if "__end__" not in stream_data:
                response.append(stream_data)
                node_response = (
                    stream_data.get('text2NoSql_node') 
                )
                finalResponse.answer = node_response.get('answer')

        if finalResponse.answer == '' and finalResponse.chart == '':
            finalResponse.answer = "Unable to process the query. Could you provide more information?"
        logger.info(f"Query processed successfully: {finalResponse.answer}")
        return finalResponse
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    try:
        logger.info("Starting the application")
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8001)
    except Exception as e:
        logger.error(f"Error starting the application: {e}")
        raise
