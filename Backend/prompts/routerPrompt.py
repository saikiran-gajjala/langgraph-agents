from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from agents.logger import setup_logger
logger = setup_logger(__name__)

system_router_prompt = (
    """You are an AI router agent responsible for classifying incoming questions. Based on your classification, the question will be routed to the appropriate team.
       There are six possible classifications:
        - QnA: For questions about fetching data related to movies, actors/casts, budgets, genres, directors, imdb and tomatoe ratings etc
        - Visualization: For questions related to data visualization, like creating or analyzing graphs, charts, and tables (not images).
        - Help: For questions related to requesting for help and guidance
        - NoContext: For questions that do not fit into any of the above categories.
                
        Your output should be **only** one of the words: QnA, Visualization, Help, or NoContext. 
        Do not include any other text. 

    """
)

members = [
    "QnA",
    "Visualization",
    "Help",
    "NoContext"]
options = [] + members


def get_router_prompt():
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_router_prompt),
            MessagesPlaceholder(variable_name="question"),
            (
                "system",
                "Given the conversation above, who should act next?"
                " Or should we FINISH? Select one of: {options}",
            ),
        ]
    ).partial(options=str(options), members=", ".join(members))
    return prompt
