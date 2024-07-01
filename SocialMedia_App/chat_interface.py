from llama_index.core import SQLDatabase
# from llama_index.llms.groq import Groq
import urllib.parse
from llama_index.core.query_engine import NLSQLTableQueryEngine

from sqlalchemy import (
    create_engine,
    
)
from llama_index.core import PromptTemplate



db_user= 'abubakar@el-technology.com'
db_password= '*l%xyG6&KhvGrspi'
db_host= 'sgs-server.database.windows.net'
db_name= 'SGS_Database'

# Construct connection string
params = urllib.parse.quote_plus('Driver={ODBC Driver 18 for SQL Server};Server=tcp:sgs-server.database.windows.net,1433;Database=SocialMediaTestDB;Uid=abubakar@el-technology.com;Pwd=*l%xyG6&KhvGrspi;Encrypt=yes;TrustServerCertificate=no;ConnectionTimeout=60;Authentication=ActiveDirectoryPassword')
# SQLAlchemy connection string
connection_string = f'mssql+pyodbc:///?odbc_connect={params}'

from sqlalchemy import create_engine, text

# Use the connection string to create a SQLAlchemy engine
engine = create_engine(connection_string)

# Test the connection and fetch some data
# Test the connection using raw SQL
# Execute query

with engine.connect() as connection:
    sql_query = text("SELECT * FROM SocialMediaData")  # Corrected SQL query
    result = connection.execute(sql_query)
    counter = 0
    for row in result:
        print(row)
        counter += 1

        if counter >= 5:
            break

from llama_index.core import SQLDatabase
sql_database = SQLDatabase(engine, include_tables=["SocialMediaData"], sample_rows_in_table_info=2)

from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding

api_key = "61cdcb9020c5433394f3be3887531f86"
azure_endpoint = "https://sgsopenai.openai.azure.com/"
api_version = "2023-07-01-preview"

llm = AzureOpenAI(
    model="gpt-35-turbo-16k",
    #model="gpt-4",
    deployment_name="gpt-35-turbo-16k",
    #deployment_name="gpt-4",
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    api_version=api_version,
)

# You need to deploy your own embedding model as well as your own chat completion model
embed_model = AzureOpenAIEmbedding(
    model="text-embedding-3-large",
    deployment_name="text-embedding-3-large",
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    api_version=api_version,
)

from llama_index.core import Settings

Settings.llm = llm
Settings.embed_model = embed_model

from llama_index.core.prompts.prompt_type import PromptType

UPDATED_TEXT_TO_SQL_TMPL = (
    "You are an expert in querying a social media database, specifically focused on Facebook account insights." 
    "Given an input question related to Facebook profiles, create a syntactically correct MSSQL query to retrieve relevant information." 
    "Then, examine the results of the query and return the answer."
    "You can order the results by a relevant column to return the most "
    "interesting examples in the database.\n\n"
    "Never query for all the columns from a specific table, only ask for a "
    "few relevant columns given the question.\n\n"
    "Pay attention to use only the column names that you can see in the schema "
    "description. "
    "Be careful to not query for columns that do not exist. "
    "Pay attention to which column is in which table. "
    "Also, qualify column names with the table name when needed. "
    "You are required to use the following format, each taking one line:\n\n"
    "Question: Question here\n"
    "SQLQuery: SQL Query to run\n"
    "SQLResult: Result of the SQLQuery\n"
    "Answer: Final answer here\n\n"
    "Only use tables listed below.\n"
    "{schema}\n\n"
    "Question: {query_str}\n"
    "SQLQuery: "
)

UPDATED_TEXT_TO_SQL_PROMPT = PromptTemplate(
    UPDATED_TEXT_TO_SQL_TMPL,
    prompt_type=PromptType.TEXT_TO_SQL,
)

table_names = ["SocialMediaData"]

sql_query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=table_names, llm=llm,
    text_to_sql_prompt=UPDATED_TEXT_TO_SQL_PROMPT
    
)

def askChatBot(query: str):
    res = sql_query_engine.query(query)
    return res.response


### Streamlit Part

import streamlit as st


# Streamlit interface
st.title("Social Media Data Chatbot")

# Input box for user question
question = st.text_input("Enter your question:", "")

# Button to submit question
if st.button("Submit"):
    # Execute the query and get the result
    answer = askChatBot(question)
    # Display the result
    st.write(answer)
