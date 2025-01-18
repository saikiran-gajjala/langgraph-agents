from typing import Literal
from langgraph.graph import StateGraph, END
from agents.mongodb_retriever import get_movies
from prompts.mongoDB_movies_Prompt import get_text2nosql_prompt
from state import MultiAgentState
from llmManager import LLMManager
from langchain_core.messages import HumanMessage
from langchain_core.runnables.graph import MermaidDrawMethod
from tools.text2NoSqlTools import text2NoSqlTools
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from agents.logger import setup_logger
import os
from langchain.memory import ConversationSummaryMemory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.memory import ChatMessageHistory

logger = setup_logger(__name__)

store = {}
session_id = "movie-session"
text2nosql_memory = ChatMessageHistory(session_id=session_id)


class WorkflowManager:
    def __init__(self, llm_manager: LLMManager):
        try:
            logger.info("Initializing WorkflowManager")
            self.llm_manager = llm_manager
            self.llm = llm_manager.llm
            self.memory = ConversationSummaryMemory(
                llm=self.llm, input_key="input", memory_key="chat_history")
            logger.info("WorkflowManager initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing WorkflowManager: {e}")
            raise

    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]

    def text2NoSql_node(self, state: MultiAgentState):
        try:
            logger.info(
                f"Processing inspection node for question: {state['question']}")
            text2NoSqlAgent = create_tool_calling_agent(
                llm=self.llm,
                prompt=get_text2nosql_prompt(),
                tools=text2NoSqlTools,
            )
            text2nosql_agent_executor = AgentExecutor(
                agent=text2NoSqlAgent,
                tools=text2NoSqlTools,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=10,
                return_intermediate_steps=False)
            agent_with_chat_history = RunnableWithMessageHistory(
                text2nosql_agent_executor,
                # This is needed because in most real world scenarios, a session id is needed
                # It isn't really used here because we are using a simple in memory ChatMessageHistory
                lambda session_id: text2nosql_memory,
                input_messages_key="input",
                history_messages_key="chat_history",
            )
            response = agent_with_chat_history.invoke(
                {"input": [HumanMessage(state['question'])]},
                config={"configurable": {"session_id": session_id}})
            return {'answer': response["output"]}
        except Exception as e:
            logger.error(f"Error in text2NoSql_node: {e}")
            raise

    def create_workflow(self) -> StateGraph:
        try:
            logger.info("Creating workflow graph")
            workflow = StateGraph(MultiAgentState)
            workflow.set_entry_point("text2NoSql_node")
            workflow.add_node("text2NoSql_node", self.text2NoSql_node)
            workflow.add_edge("text2NoSql_node", END)

            logger.info("Workflow graph created successfully")
            return workflow
        except Exception as e:
            logger.error(f"Error creating workflow graph: {e}")
            raise

    def generate_graph(self):
        try:
            logger.info("Generating workflow graph")
            memory = MemorySaver()
            enableDebugging = os.getenv("ENABLE_DEBUGGING") == "true"
            graph = self.create_workflow().compile(
                checkpointer=memory, debug=enableDebugging)
            graph.name = "Text To NoSQL Graph"
            # Draw the graph and get the bytes
            image_bytes = graph.get_graph().draw_mermaid_png(
                draw_method=MermaidDrawMethod.API,
            )

            # Save the bytes to an image file
            with open("workflow_graph.png", "wb") as image_file:
                image_file.write(image_bytes)
            logger.info("Workflow graph generated successfully")
            return graph
        except Exception as e:
            logger.error(f"Error generating workflow graph: {e}")
            raise
