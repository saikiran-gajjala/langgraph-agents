from pymongo import MongoClient
from langchain.chains import LLMChain
from llmManager import LLMManager
from langchain.memory import ConversationBufferMemory
from datetime import datetime
from prompts.mongoDB_movies_Prompt import get_movies_collection_prompt, movies_collection_schema , examples
from agents.logger import setup_logger
import re
import os
import json

logger = setup_logger(__name__)

client = MongoClient(os.getenv('MONGODB_CONNECTION_STRING'))
db = client[os.getenv('MONGODB_DATABASE_NAME')]
collection = db["movies"]
llm = LLMManager().llm
memory = ConversationBufferMemory(
    llm=llm, input_key="user_question", memory_key="chat_history",  return_messages=True)

nosql_llm_chain = LLMChain(
    llm=llm, prompt=get_movies_collection_prompt(), verbose=True, memory=memory)

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
                "movies_collection_schema": movies_collection_schema,
                "examples": examples
            })
        iso_date_pattern = re.compile(r'ISODate\("([^"]+)"\)')
        query_modified = re.sub(
            iso_date_pattern, iso_date_replacer, response['text'])  
        query_modified = query_modified.replace('null', 'None').replace(
            '```json', '').replace('```', '').replace('\n', '').replace('mongodb','')
        if 'Output:' in query_modified:
            query_modified = query_modified.split('Output: ')[1]
        try:
            # Safely parse the modified query string
            pipeline = eval(query_modified)
        except Exception as e:
            logger.error(f"JSON decode error: {e}")
            logger.error(f"Query: {query_modified}")
            pipeline = json.loads(query_modified)

        logger.info(f"Query generated: {pipeline}")
        results = collection.aggregate(pipeline)
        documents = []
        for doc in results:
            documents.append(doc)
            doc.pop('_id', None)
        return documents
    except Exception as e:
        logger.error(f"Error retrieving movies: {e}")
        raise
