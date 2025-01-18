from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from datetime import datetime
from bson import json_util
from agents.logger import setup_logger

logger = setup_logger(__name__)
examples = """
        Input1: Get me movies with an IMDb rating above 8 and more than 10,000 votes.
        Output1: [ { "$match": { "imdb.rating": { "$gt": 8 }, "imdb.votes": { "$gt": 10000 } } } ]

        Input2: Can you list movies that are in the 'Action' and 'Adventure' genres?
        Output2: [ { "$match": { "genres": { "$all": ["Action", "Adventure"] } } } ]
        
        Input3: What is the average IMDb rating for 'Comedy' genre movies?
        Output3: [ { "$match": { "genres": "Comedy" } }, { "$group": { "_id": null, "averageRating": { "$avg": "$imdb.rating" } } } ]
        
        Input4: Find me movies that feature 'A.C. Abadie' and belong to the 'Western' genre and also fetch poster and plot of the movies
        Output4: [ { "$match": { "cast": "A.C. Abadie", "genres": "Western" } }, { "$project": { "poster": 1, "plot": 1 } } ]
        
        Input5: Can you get me the latest movies with a Rotten Tomatoes critic rating above 7 and a viewer rating above 4.
        Output5: [ { "$match": { "tomatoes.critic.rating": { "$gt": 7 }, "tomatoes.viewer.rating": { "$gt": 4 } } }, { "$sort": { "lastupdated": -1 } } ]
        
        Input6: Show me movies from the 2000s that have won at least 3 awards.
        Output6: [ { "$match": { "year": { "$gte": 2000, "$lt": 2010 }, "awards.wins": { "$gte": 3 } } } ]

"""
movies_collection_schema = """
            - **_id** (Unique Identifier): A unique identifier for each movie.  
            - **plot** (Short Storyline): A brief summary of the movie's plot.  
            - **genres** (Array of Strings): List of genres associated with the movie.  
            - **runtime** (Number): Duration of the movie in minutes.  
            - **cast** (Array of Strings): List of actors in the movie.  
            - **poster** (String): URL for the movie's poster image.  
            - **title** (String): The title of the movie.  
            - **fullplot** (String): A detailed summary of the movie's storyline.  
            - **languages** (Array of Strings): List of languages the movie is available in.  
            - **released** (Date): Release date of the movie.  
            - **directors** (Array of Strings): List of directors who directed the movie.  
            - **rated** (String): Age rating of the movie (e.g., TV-G, PG-13).  
            - **awards** (Object): Contains details about awards the movie has received:  
              - **wins** (Number): Number of awards won.  
              - **nominations** (Number): Number of nominations.  
              - **text** (String): Summary of awards in text form.  
            - **lastupdated** (String): The last time the movie's data was updated.  
            - **year** (Number): Year the movie was released.  
            - **imdb** (Object): Contains IMDb data:  
              - **rating** (Number): IMDb rating of the movie.  
              - **votes** (Number): Total number of votes received on IMDb.  
              - **id** (Number): IMDb movie ID.  
            - **countries** (Array of Strings): List of countries where the movie was produced.  
            - **type** (String): Type of content (e.g., movie, series).  
            - **tomatoes** (Object): Contains Rotten Tomatoes data:  
              - **viewer** (Object): Contains viewer-related data:  
                - **rating** (Number): Viewer rating out of 5.  
                - **numReviews** (Number): Total number of viewer reviews.  
                - **meter** (Number): Viewer approval percentage.  
              - **critic** (Object): Contains critic-related data:  
                - **rating** (Number): Critic rating out of 10.  
                - **numReviews** (Number): Total number of critic reviews.  
                - **meter** (Number): Critic approval percentage.  
              - **fresh** (Number): Number of "Fresh" ratings.  
              - **rotten** (Number): Number of "Rotten" ratings.  
              - **lastUpdated** (Date): Last time Rotten Tomatoes data was updated.  
            - **num_mflix_comments** (Number): Number of comments on the movie.  
    """

movies_mongodb_prompt = """You are an intelligent AI assistant who is expert in transforming natural language questions into mongodb aggregation pipeline queries.
      Your task is to accurately generate MongoDB aggregation pipeline using the provided schema.
    **Schema Description**:
       The mentioned mongodb collection talks about various movies and their details.
       The schema for this document represents the structure of the data, describing various properties related to the movies, ratings, plot/story, cast/actors and genres.
    {movies_collection_schema}
    
    **Examples**:
    {examples}
    **Important Instructions**:
    - All dates must be in ISODate bson type and don't use '$date' in queries.
    - **You must return the query as to use in aggregation pipeline nothing else.No additional explanations or text.**
    - Always exclude or project redundant fields by using $project stage in the pipeline and only include the required fields, fields in $match stage
    - If the user question requests a count of matching documents, use the $count stage appropriately.
    - Always limit the number of documents returned in the query to 20 using the $limit stage.
    """


# def get_movies_collection_prompt():
#     query_with_prompt_template = PromptTemplate(
#         template=movies_mongodb_prompt,
#         input_variables=["user_question", "movies_collection_schema"]
#     ).partial(present_date=datetime.now())
#     return query_with_prompt_template


def get_movies_collection_prompt():
    prompt = ChatPromptTemplate.from_messages(
        [
          SystemMessagePromptTemplate.from_template(movies_mongodb_prompt),
          MessagesPlaceholder(variable_name="chat_history"),
          HumanMessagePromptTemplate.from_template("{user_question}")
        ])
    return prompt


def get_text2nosql_prompt():
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                    You are a helpful assistant that quickly evaluates user input and selects appropriate tools to generate a response efficiently. Format the output in CommonMark Markdown, using:
                    - Headers: Use ## for titles and section headers.
                    - Text: Organize into paragraphs, bullet points, tables, and bold text as needed.
                    - Media: Embed images, links, or URLs as appropriate for clarity.
                    - etc.
                    Ensure a concise, accurate response.
                    The current date is {present_date}.
                """,
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    prompt = prompt.partial(present_date=datetime.now().strftime("%Y-%m-%d"))
    return prompt
