import boto3
from botocore.config import Config
from langchain.llms.bedrock import Bedrock
from langchain.embeddings import BedrockEmbeddings
import pprint
import streamlit as st
import logging 
import json
import os,sys
import re
sys.path.append('/home/sagemaker-user/demo/')
import time
import pandas as pd
import io
from boto_client import Clientmodules
from llm_basemodel2 import LanguageModel
from athena_execution import AthenaQueryExecute
from vector_embedding_client_product import EmbeddingBedrock
from sql_formatter.core import format_sql
import importlib.util
import inspect
from src.utils import *


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
session = boto3.session.Session()
bedrock_client = session.client('bedrock')
rqstath=AthenaQueryExecute()
comprehend_client = session.client('comprehend')
eb = EmbeddingBedrock()

eb_load = eb.load_local_vector_store(vector_store_path=r'/home/sagemaker-user/demo/vector_store_client_product/23072024121127.vs')
# eb_load = eb.load_local_vector_store(vector_store_path=r'/home/sagemaker-user/text-to-sql-for-athena/vector_store_client_product/22072024182912.vs')
# eb_load = eb.load_local_vector_store(vector_store_path=r'/home/sagemaker-user/text-to-sql-for-athena/vector_store/20062024133050.vs')
from inspect import cleandoc
class RequestQueryBedrock:
    def __init__(self):
        # self.model_id = "anthropic.claude-v2"
        self.bedrock_client = Clientmodules.createBedrockRuntimeClient()
        self.language_model = LanguageModel(self.bedrock_client)
        self.llm = self.language_model.llm
    def getEmbedding(self,user_query):
        vcindxdoc=eb_load
        documnet=eb.getSimilaritySearch(user_query,vcindxdoc)
        return eb.format_metadata(documnet)
        
    def generate_sql(self,prompt, max_attempt=2) ->str:
            """
            Generate and Validate SQL query.

            Args:
            - prompt (str): Prompt is user input and metadata from Rag to generating SQL.
            - max_attempt (int): Maximum number of attempts correct the syntax SQL.

            Returns:
            - string: Sql query is returned .
            """
            attempt = 0
            error_messages = []
            prompts = [prompt]

            while attempt < max_attempt:
                logger.info(f'Sql Generation attempt Count: {attempt+1}')
                try:
                    logger.info(f'we are in Try block to generate the sql and count is :{attempt+1}')
                    generated_sql = self.llm.invoke(prompt).content
                    # print(generated_sql)
                    query_str = generated_sql.split("```")[1]
                    query_str = " ".join(query_str.split("\n")).strip()
                    query_str = query_str.replace('`','"')
                    print('query: '+query_str)
                    sql_query = query_str[3:] if query_str.startswith("sql") else query_str
                    
                    explanation = query_str = generated_sql.split("```")[2]
                    print('explanation: '+explanation)
                    
                    
                    # return sql_query
                    syntaxcheckmsg=rqstath.syntax_checker(sql_query)
                    if syntaxcheckmsg=='Passed':
                        logger.info(f'syntax checked for query passed in attempt number :{attempt+1}')
                        return sql_query,explanation
                    else:
                        prompt = f"""{prompt}
                        This is syntax error: {syntaxcheckmsg}. 
                        To correct this, please generate an alternative SQL query which will correct the syntax error for Athena.
                        The updated query should take care of all the syntax issues encountered.
                        Follow the instructions mentioned above to remediate the error. 
                        Update the below SQL query to resolve the issue:
                        {sqlgenerated}
                        Make sure the updated SQL query aligns with the requirements provided in the initial question."""
                        prompts.append(prompt)
                        attempt += 1
                except Exception as e:
                    logger.error('FAILED')
                    msg = str(e)
                    error_messages.append(msg)
                    attempt += 1
            return sql_query,explanation

rqst=RequestQueryBedrock()

def userinput(user_query):
    logger.info(f'Searching metadata from vector store')
    # vector_search_match=rqst.getEmbeddding(user_query)
    vector_search_match=rqst.getEmbedding(user_query)
    # print(vector_search_match)
    # details="It is important that the SQL query complies with Athena syntax.For date columns comparing to string , please cast the string input as date. It is important to not use alias for group by clause, if select has DATE_FORMAT then use DATE_FORMAT in the group by. It is also important to respect the type of columns: if a column is string, the value should be enclosed in quotes. If you are writing CTEs then include all the required columns. While concatenating a non string column, make sure cast the column to string. "
    
        
    # final_question = "\n\nHuman:"+details + vector_search_match + user_query+ "n\nAssistant:"
    final_question =f""" You are an AI assistant that converts natural language questions into SQL query complies with Athena syntax.
            Important notes: It is important that the SQL query complies with Athena syntax.For date columns comparing to string , please cast the string input as date. It is important to not use alias for group by clause. It is also important to respect the type of columns: if a column is string, the value should be enclosed in quotes. If you are writing CTEs then include all the required columns. While concatenating a non string column, make sure cast the column to string.

            Database tables information:
            {vector_search_match}

            User question: {user_query}
                """
    
    answer,explanation = rqst.generate_sql(final_question)
    return answer,explanation

def text_to_sql_func(user_query:str):
    check_pii = comprehend_client.contains_pii_entities(Text=user_query,LanguageCode="en")
    # convert to df for the labels
    df = pd.DataFrame(check_pii.get('Labels'))
    # filter to where scores>0.9
    if df.shape[0]>100000:
        df = df[df['Score']>=0.9]
    if df.shape[0]>100000:
        querygenerated = f"Query contains the following PII: {df['Name'].unique().__str__()}"
        QueryOutput = pd.DataFrame()
        explanation=''
    else:
        try:
            querygenerated,explanation=userinput(user_query)
            # QueryOutput=rqstath.execute_query(querygenerated)
        except: 
            querygenerated = 'Cannot Generate Query' 
            explanation=''
            # QueryOutput = pd.DataFrame()
    return querygenerated,explanation

def fetch_results(querygenerated):
    if querygenerated== 'Cannot Generate Query' :
        return  pd.DataFrame()
    else:
        return rqstath.execute_query(querygenerated)
