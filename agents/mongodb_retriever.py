from pymongo import MongoClient
from langchain.chains import LLMChain
from llmManager import LLMManager
from langchain.memory import ConversationSummaryMemory
from datetime import datetime
from prompts.mongoDB_movies_Prompt import get_text2nosql_prompt, movies_collection_schema
from agents.logger import setup_logger
import re
import os
import json

logger = setup_logger(__name__)

client = MongoClient(os.getenv('MONGODB_CONNECTION_STRING'))
db = client[os.getenv('MONGODB_DATABASE_NAME')]
collection = db["movies"]
llm = LLMManager().llm
memory = ConversationSummaryMemory(
    llm=llm, input_key="user_question", memory_key="movies_chat_history")

nosql_llm_chain = LLMChain(
    llm=llm, prompt=get_text2nosql_prompt(), verbose=True, memory=memory)


def iso_date_replacer(match):
    iso_date_str = match.group(1)
    # Convert the extracted string into a Python datetime object
    return f'datetime.fromisoformat("{iso_date_str[:-1]}")'

def get_movies(query):
    try:
        logger.info(f"Executing query: {query}")
        response = nosql_llm_chain.invoke(
            {
                "user_question": query,
                "collection_schema": movies_collection_schema
            })
        iso_date_pattern = re.compile(r'ISODate\("([^"]+)"\)')
        query_modified = re.sub(
            iso_date_pattern, iso_date_replacer, response['text'])
        query_modified = query_modified.replace('null', 'None').replace(
            '```json', '').replace('```', '').replace('\n', '')
        try:
            # Safely parse the modified query string
            pipeline = eval(query_modified)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            logger.error(f"Query: {query_modified}")
            pipeline = json.loads(query_modified)

        logger.info(f"Query generated: {pipeline}")
        pipeline.append({
            "$project": {"audit": 0}
        })
        results = collection.aggregate(pipeline)
        documents = []
        for doc in results:
            documents.append(doc)
        return documents
    except Exception as e:
        logger.error(f"Error retrieving movies: {e}")
        raise
