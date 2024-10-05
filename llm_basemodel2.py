from langchain.llms.bedrock import Bedrock
from langchain.embeddings import BedrockEmbeddings
from langchain_community.chat_models import BedrockChat
from langchain_aws import ChatBedrock
import boto3
class LanguageModel():
    def __init__(self,client):
        # self.bedrock_client = client
        # claude v3
        self.bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name='us-east-1',
)
        ############
        # Anthropic Claude     
        # Bedrock LLM
        inference_modifier = {
                "max_tokens": 3000,
                "temperature": 0.0,
                # "top_k": 20,
                # "top_p": 1,
                # "stop_sequences": ["\n\nHuman:"],
            }
        self.llm = ChatBedrock(
            # model_id = "anthropic.claude-3-haiku-20240307-v1:0",
                           model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0",
                            client = self.bedrock_client, 
                            model_kwargs = inference_modifier 
                            )

        
        # Embeddings Modules
        self.embeddings = BedrockEmbeddings(
            client=self.bedrock_client, 
            model_id="amazon.titan-embed-text-v1"
        )

class LanguageModel_titantext():
    def __init__(self,client):
        # self.bedrock_client = client
        # claude v3
        self.bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name='us-east-1',
)
        ############
        # Anthropic Claude     
        # Bedrock LLM
        inference_modifier = {
                "max_tokens": 3000,
                "temperature": 0.0,
                "top_k": 20,
                "top_p": 1,
                "stop_sequences": ["\n\nHuman:"],
            }
        self.llm = ChatBedrock(
            # model_id = "anthropic.claude-v2:1",
                           model_id = "amazon.titan-text-premier-v1:0",
                            client = self.bedrock_client, 
                            model_kwargs = inference_modifier 
                            )

        
        # Embeddings Modules
        self.embeddings = BedrockEmbeddings(
            client=self.bedrock_client, 
            model_id="amazon.titan-embed-text-v1"
        )
