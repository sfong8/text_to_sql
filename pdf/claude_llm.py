import boto3
from langchain_community.chat_models import BedrockChat
session = boto3.session.Session()
bedrock_client = session.client('bedrock-runtime')

def claude3_llm():
    inference_modifier = {
            "temperature": 0.01,
            "top_k": 20,
            "top_p": 1,
            "stop_sequences": ["\n\nHuman:"],
        }
    
    llm = BedrockChat(
        # model_id = "anthropic.claude-v2:1",
                       model_id = "anthropic.claude-3-haiku-20240307-v1:0",
        # model_id ='anthropic.claude-3-5-sonnet-20240620-v1:0',
                        client = bedrock_client, 
                        model_kwargs = inference_modifier 
                        )
    return llm

