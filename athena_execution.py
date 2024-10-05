import logging 
import json
import os,sys
import re
sys.path.append('/home/sagemaker-user/demo/')
import time
import pandas as pd
import io
from boto_client import Clientmodules
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class AthenaQueryExecute:
    def __init__(self):
        self.glue_databucket_name='llm-athena-output'
        self.athena_client=Clientmodules.createAthenaClient()
        self.s3_client=Clientmodules.createS3Client()
    
    def execute_query(self, query_string):
        result_folder='llm-athena-output/athena_output'
        result_config = {"OutputLocation": f"s3://bedrock-example-simonfong/llm-athena-output/athena_output"}
        query_execution_context = {
            "Catalog": "AwsDataCatalog",
        }
        
        query_execution = self.athena_client.start_query_execution(
            QueryString=query_string,
            ResultConfiguration=result_config,
            QueryExecutionContext=query_execution_context,
        )
        execution_id = query_execution["QueryExecutionId"]
        time.sleep(3)

        # self.wait_for_execution(execution_id)
        file_name = f"{result_folder}/{execution_id}.csv"
        logger.info(f'checking for file :{file_name}')
        local_file_name = f"/tmp/{file_name}"

        print(f"Calling download fine with params {local_file_name},{file_name}")
        obj = self.s3_client.get_object(Bucket= 'bedrock-example-simonfong' , Key = file_name)
        df = pd.read_csv(io.BytesIO(obj['Body'].read()), encoding='utf8')
        return df
        
    def syntax_checker(self,query_string):
        # print("Inside execute query", query_string)
        query_result_folder='athena_query_output'
        query_config = {"OutputLocation": f"s3://bedrock-example-simonfong/llm-athena-output/athena_query_output/"}
        query_execution_context = {
            "Catalog": "AwsDataCatalog",
        }
        query_string="Explain  "+query_string
        print(f"Executing: {query_string}")
        try:
            print(" I am checking the syntax here")
            query_execution = self.athena_client.start_query_execution(
                QueryString=query_string,
                ResultConfiguration=query_config,
                QueryExecutionContext=query_execution_context,
            )
            execution_id = query_execution["QueryExecutionId"]
            print(f"execution_id: {execution_id}")
            time.sleep(2)
            results = self.athena_client.get_query_execution(QueryExecutionId=execution_id)
            # print(f"results: {results}")
            status=results['QueryExecution']['Status']
            print("Status :",status)
            if status['State']=='SUCCEEDED':
                return "Passed"
            else:  
                print(results['QueryExecution']['Status']['StateChangeReason'])
                errmsg=results['QueryExecution']['Status']['StateChangeReason']
                return errmsg
            # return results
        except Exception as e:
            print("Error in exception")
            msg = str(e)
            print(msg)