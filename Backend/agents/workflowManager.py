from langgraph.graph import StateGraph, END
from agents.mongodb_retriever import get_movies
from agents.plot_generator import generate_chart_based_on_query, generate_mongo_query, rephrase_user_query_for_visualization
from models.models import QueryResponse
from prompts.mongoDB_movies_Prompt import get_text2nosql_prompt
from prompts.routerPrompt import get_router_prompt
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
from langchain.memory import ConversationSummaryMemory
from langchain_core.runnables.history import RunnableWithMessageHistory
import os

logger = setup_logger(__name__)

store = {}
session_id = "movie-session"
text2nosql_memory = ChatMessageHistory(session_id=session_id)


class WorkflowManager:
    def __init__(self, llm_manager: LLMManager):
        try:
            logger.info("Initializing WorkflowManager")
            self.llm_manager = llm_manager
            self._llm = llm_manager.llm
            self._slm = llm_manager.slm
            self.memory = ConversationSummaryMemory(
                llm=self._llm, input_key="input", memory_key="chat_history")
            self.graph = self._initialize_workflow()
            logger.info("WorkflowManager initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing WorkflowManager: {e}")
            raise

    def invoke(self, query) -> QueryResponse:
        """
        Processes a query by streaming data through a graph and returns a response.

        Args:
            query (str): The query to be processed.

        Returns:
            QueryResponse: An object containing the answer and chart generated from the query.

        The function initializes a QueryResponse object with default values and sets up the configuration
        for the graph streaming. It then streams data through the graph using the provided query and configuration.
        The streamed data is processed to extract responses from different nodes. If a response is found in the
        'text2NoSql_node', it is set as the answer. If a response is found in the 'visualization_node',
        'generate_mongo_query_node', or 'generate_chart_node', it is set as the chart. If no answer or chart is found,
        a default message is set in the answer.

        Raises:
            Any exceptions raised by the graph streaming process.
        """
        finalResponse = QueryResponse(answer='', chart='')
        config = {"configurable": {"thread_id": "1"}, "recursion_limit": 100}
        input = {"question": query}
        response = []
        for stream_data in self.graph.stream(input, config):
            if "__end__" not in stream_data:
                response.append(stream_data)
                if (stream_data.get('router_node')):
                    continue
                node_response = (
                    stream_data.get('text2NoSql_node')
                )
                visualization_response = (
                    stream_data.get('visualization_node') or
                    stream_data.get('generate_mongo_query_node') or
                    stream_data.get('generate_chart_node')
                )
                if node_response:
                    finalResponse.answer = node_response.get('answer')
                elif visualization_response:
                    finalResponse.chart = visualization_response.get('chart')
        if finalResponse.answer == '' and finalResponse.chart == '':
            finalResponse.answer = "Unable to process the query. Could you provide more information?"
        return finalResponse

    def _initialize_workflow(self):
        try:
            logger.info("Generating workflow graph")
            memory = MemorySaver()
            enableDebugging = os.getenv("ENABLE_DEBUGGING") == "true"
            graph = self._create_workflow().compile(
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

    def _router_agent(self, state: MultiAgentState):
        try:
            logger.info(f"Routing question: {state['question']}")
            supervisor_chain = get_router_prompt() | self._slm
            messages = [HumanMessage(state['question'])]
            response = supervisor_chain.invoke({"question": messages})

            if 'content_filter_result' in response:
                logger.warning(
                    "The response was filtered due to content management policy.")
                return {"question_type": "Error", 'messages': messages}

            logger.info(f"Routing to: {response.content}")
            return {"question_type": response.content, 'messages': messages}
        except Exception as e:
            logger.error(f"Error in router_agent: {e}")
            raise

    def _text2NoSql_node(self, state: MultiAgentState):
        try:
            logger.info(
                f"Processing inspection node for question: {state['question']}")
            text2NoSqlAgent = create_tool_calling_agent(
                llm=self._llm,
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

    def _route_question(self, state: MultiAgentState):
        try:
            logger.info(f"Routing question: {state['question_type']}")
            return state['question_type']
        except Exception as e:
            logger.error(f"Error in route_question: {e}")
            raise

    def _no_context_node(self, state: MultiAgentState):
        logger.info("Processing no context node")
        return {"answer": 
            """I'm sorry, I don't understand the question. 
                Please provide more context or rephrase your question.
            """}

    def _create_workflow(self) -> StateGraph:
        try:
            logger.info("Creating workflow graph")
            workflow = StateGraph(MultiAgentState)
            self._add_nodes_to_workflow(workflow)
            self._add_edges_to_workflow(workflow)
            logger.info("Workflow graph created successfully")
            return workflow
        except Exception as e:
            logger.error(f"Error creating workflow graph: {e}")
            raise

    def _add_nodes_to_workflow(self, workflow):
        workflow.add_node("router_node", self._router_agent)
        workflow.set_entry_point("router_node")
        workflow.add_node("text2NoSql_node", self._text2NoSql_node)
        workflow.add_node(
            "visualization_node",
            rephrase_user_query_for_visualization)
        workflow.add_node(
            "generate_mongo_query_node",
            generate_mongo_query)
        workflow.add_node(
            "generate_chart_node",
            generate_chart_based_on_query)
        workflow.add_node("no_context_node", self._no_context_node)

    def _add_edges_to_workflow(self, workflow):
        workflow.add_edge("text2NoSql_node", END)
        workflow.add_edge(
            "visualization_node",
            "generate_mongo_query_node")
        workflow.add_edge(
            "generate_mongo_query_node",
            "generate_chart_node")
        workflow.add_edge("generate_chart_node", END)
        workflow.add_edge("no_context_node", END)
        workflow.add_conditional_edges(
            "router_node",
            self._route_question,
            {
                'QnA': 'text2NoSql_node',
                'Visualization': 'visualization_node',
                'NoContext': 'no_context_node'
            }
        )
