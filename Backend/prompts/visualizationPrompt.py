from langchain.prompts import PromptTemplate
from agents.logger import setup_logger

logger = setup_logger(__name__)

user_query_regenerate_prompt = """
        You are an expert in generating MongoDB queries based on the schema of a collection and the user's intent.
        Based on the original user query (which is related to visualizing data) and the schema provided,
        you need to generate a new user query that can retrieve the required data for visualization.
        Always think and consider if the question is asked for a time series or trend charts.

        **Schema Context**:
        - The collection schema represents various aspects of movies data, such as movie information, actors/casts, budgets, genres, directors, imdb ratings etc.

        **Original User Query**:
        "{user_query}"

        **Collection Schema**:
        {collection_schema}

        Your task is to:
        - Understand the original user query and identify what data is required for visualization.
        - Based on the user's request and the schema context, generate a relevant new query that can fetch the required data from the collection.

        **Examples**:

        Example 1:
        - **Original User Query**: "Show me the number of actors count for each movies"
        - **Generated Query**: "Retrieve movies and their associated actors to visualize actors counts per movie."

        Example 2:
        - **Original User Query**: "Generate a scatter plot comparing the imdb ratings found in each movie"
        - **Generated Query**: "Retrieve all movies with their number of imdb ratings, to visualize a scatter plot comparing the two fields."

        Example 3:
        - **Original User Query**: "Show me a line plot of movie trends over the past three months, with a breakdown by genre"
        - **Generated Query**: "Retrieve all movies updated in the past three months, including timestamps and statuses, to visualize movie trends by genre."

        Note:
            1. Just return the generated query string as the final output.
            2. The generated query should be plain text, not MongoDB Query.
        """


def create_query_generation_prompt():
    query_generation_prompt_template = PromptTemplate(
        template=user_query_regenerate_prompt,
        input_variables=["user_query", "collection_schema"]
    )
    return query_generation_prompt_template


python_code_generation_prompt = """
        You are an expert Python programmer specializing in data visualization using Plotly, Pandas, and Numpy. 
        Your task is to generate Python code that creates a plot based on the user's query and the provided data. 
        You can choose to convert the data into a Pandas DataFrame if needed.

        **Context**:
        - The data is retrieved from a MongoDB collection as JSON and passed as an argument to the function.
        - The metadata and a sample of the retrieved data are provided below. You **must only** refer to the data described in the metadata.

        **Metadata of the retrieved data:**
        - Columns: {column_names}
        - Number of rows: {number_of_rows}
        - Sample record: {sample_record}

        **User query**:
        "{user_query}"

        **Your task**:
        - Generate Python code that defines a function `generate_plot(data)` which:
            1. Accepts the retrieved data (`data`) as an argument.
            2. **Convert any `ObjectId` fields to strings** before processing the data only if the provided columns contains _id or ObjectId fields.
            3. You can choose to convert the data to a Pandas DataFrame or Numpy data if that simplifies the task.
            4. If the user query specifies a particular type of plot (e.g., bar plot, scatter plot, line plot), use that specific plot type.
            5. If the user query does not specify a plot type, analyze the query and data and choose the best-fitting plot type.
            6. **Convert any `Period` types to strings** before creating the plot to avoid serialization issues.
            7. Generates the plot based on the user query and **returns the plot object (`fig`)**. Do not save the plot to a file or display it.
            8. Always generate the charts in dark mode for better visualization unless specified by the user otherwise. Must use layout i.e template='plotly_dark' for dark mode. 
            9. Automatically calls the `generate_plot(data)` function after defining it, passing the `data` argument to it. **Don't fill `data` argument with any sample value. Just pass it as it is**
            10. Stores the generated plot object with name `fig`
            11. Always include necessary imports at the beginning of the code.
            12. Very important that you must only use the columns provided in the metadata of the retrieved data. Do not include any additional columns.

        **Important Instructions:**
        - Don't generate sample data in the code. Accept the data as an argument to the `generate_plot(data)` function.
        - The input data has a specific structure that you **must strictly follow**.
        - The collection schema is only for your understanding and context. Do **not** use it to infer any extra columns.
        - If any field or column is missing from the retrieved data, handle the case appropriately (e.g., handle missing values, or give an appropriate error).
        - Generate the Python code such that it strictly follows the input data format provided below.
        - You must return python code block with valid Python code with no syntax errors.
        - Ensure no extra space before the backticks of the code block.
        
        **Code Requirements**:
        - The code should leverage best practices for working with data in Python, including:
            - Ensuring the correct mapping of data fields to the plot axes.
            - Handling edge cases such as missing or incomplete data.
            - Using appropriate axis labels, plot titles, and legends.
            - There should not be any syntax errors in the generated code.
        - You must **strictly** follow the structure of the data provided in the metadata.
        - The input data is already filtered based on the user query, so you can directly use it for preprocessing and plotting.
        """

def create_code_generation_prompt():
    code_generation_prompt_template = PromptTemplate(
        template=python_code_generation_prompt,
        input_variables=["column_names", "number_of_rows",
                         "sample_record", "collection_schema", "user_query"]
    )
    return code_generation_prompt_template
