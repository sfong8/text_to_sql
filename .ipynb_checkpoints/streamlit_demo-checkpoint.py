import sys
import streamlit as st
sys.path.append('/home/sagemaker-user/demo/')
from text_to_sql_script_demo import text_to_sql_func,fetch_results
from sql_formatter.core import format_sql
import sys
import pandas as pd 
import seaborn as sns
from dataframe_agent import dataframe_agent
import datetime
import time
import os
import numpy as np
from sql_text import defined_prompts
if 'clicked' not in st.session_state:
    st.session_state.clicked = False
if 'show_chart_reset' not in st.session_state:
    st.session_state.show_chart_reset = None
if 'dataframe_query' not in st.session_state:
    st.session_state.dataframe_query = ''
def click_queryDF():
    st.session_state.queryDataFrame = True
def click_button():
    st.session_state.clicked = True
def click_button_reverse():
    st.session_state.clicked = False
import os 
def get_image_file():
    master_df = pd.DataFrame()
    for file in os.listdir('/home/sagemaker-user/demo/'):
        if file.endswith ('.png'):
            time_mod =datetime.datetime.fromtimestamp( os.path.getmtime(f'/home/sagemaker-user/demo/{file}'))
            temp_df = pd.DataFrame([file,time_mod]).T
            temp_df.columns = ['file_name','time']
            master_df = pd.concat([master_df,temp_df])
    master_df = master_df.sort_values(by=['time'], ascending=False).reset_index(drop=True)
    return master_df['file_name'][0]
st.set_page_config(layout="wide")    
st.title("Text to SQL - Query data using Natural Language")
st.markdown(
    """This demo illustrates how to retrieve data from databases and analyse results using natural language
    \nNote: Demo only uses Synthetic data"""
)


with st.chat_message("user"):
    initial_options =  [  "show me the total monthly income and balance by parent company",
                        'show me the monthly income and balance for parent "parent company abc"',
  
    "show me monthly income by client name and product level 2 for RD John Smith"]
    init_prompt = st.selectbox(
    'You might want to try these prompts...',
   initial_options
)
    with st.form("my_form"):

        st.text_input('Enter your query',init_prompt,key='free_text')
        submitted = st.form_submit_button("Submit")

    
    if submitted or st.session_state.show_chart_reset:
        user_prompt = st.session_state.free_text
        st.write('User Prompt: ' + user_prompt)
        with st.spinner('Generating SQL and Fetching Results'):
            
            if st.session_state.free_text in initial_options:
            
                time.sleep(np.random.randint(5,10))
                result_dict = defined_prompts.get(st.session_state.free_text)
                print('test')
                sql_query = result_dict.get('sql_query')
                explanation = result_dict.get('explanation')
                result = pd.read_csv(result_dict.get('results'))
                query_results_options = list(result_dict.get('query_questions').keys())
                
            else:        
                sql_query,explanation  = text_to_sql_func(user_query=user_prompt)
                sql_query = format_sql(sql_query)
                if sql_query=='Cannot Generate Query':
                        st.error('Error!')
                        st.text(sql_query + ', Please try again')
                else:
                        result = fetch_results(sql_query)
                query_results_options=['Generate me some insights into the income by product and client',
                    "which client had a decrease in total income in the latest month?",
                    "plot a barchart for the total income by client"]
            st.success('Done!')
            st.markdown('##### Generated SQL:')
            # st.session_state.dataframe_query= ''
            st.code(sql_query,language='sql')
            st.markdown('##### Explanation:')
            st.text(explanation)
            with st.spinner('Fetching Results'):
                with st.expander("Returned Result:",expanded=True):
                    st.markdown('##### Returned Result:')
                    st.dataframe(result)
                    # st.download_button(label="Download data as CSV",data= result  ,file_name="query_results.csv", mime="text/csv")
                    st.session_state.result=result
                init_prompt2 = st.selectbox(
                    'You might want to try these prompts...',
                    query_results_options
                )
                with st.form("my_form2"):
                      
                    st.text_input('Query returned result',init_prompt2,key= 'dataframe_query')
                    submitted2 = st.form_submit_button("Submit")
            
                # result.to_csv('test_result2.csv',index=None)
        st.session_state.show_chart_reset=True
        if submitted2:
            if len(st.session_state.dataframe_query)>0:
                with st.spinner('Generating response'):
                    if  st.session_state.free_text in initial_options and st.session_state.dataframe_query in query_results_options:
                        query_questions =  result_dict.get('query_questions')
                        result_query = query_questions.get(st.session_state.dataframe_query)
                        if 'png' in result_query:
                            st.image(result_query)
                        else:
                            st.markdown(result_query)
                    else:
                        agent = dataframe_agent(st.session_state.result)
                        if 'chart' or 'charts' or 'graph' or 'graphs' or 'plot' or 'plt' in st.session_state.dataframe_query:
                            output = agent.invoke(st.session_state.dataframe_query+". If any charts or graphs or plots were created save them localy and include the save file names in your response. Remember to set pandas option to pd.set_option('display.float_format', str). You must use all rows of the dataframe.",verbose=False).get('output')
                            
                            png_file = [x for x in output.split("'") if 'png' in x][0]
                            
                            time.sleep(5)
                            # st.text(get_image_file())
                            st.image(get_image_file())
                            st.text('Chat output: ' + output)
                        else:
                            output = agent.invoke(st.session_state.dataframe_query,verbose=False).get('output')
                            st.markdown(output)
                            



