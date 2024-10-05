from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_aws import ChatBedrock
import boto3
from langchain.agents import AgentType
import pandas as pd
def dataframe_agent(text:pd.DataFrame()):
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name='us-east-1',
    )
    # model_id = 'anthropic.claude-3-haiku-20240307-v1:0'
    model_id = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
    model_kwargs =  { 
        "max_tokens": 1000,
        "temperature": 0.0,
    }
    claude_3_client = ChatBedrock(
        client=bedrock_runtime,
        model_id=model_id,
        model_kwargs=model_kwargs,
    )
    agent = create_pandas_dataframe_agent(claude_3_client, df=text,verbose=True,allow_dangerous_code=True,max_iterations=5,number_of_head_rows=500,handle_parsing_errors=True)
    return agent
