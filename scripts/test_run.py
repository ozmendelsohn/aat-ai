import panel as pn
from chat.llm_chat import LLMConversation
from run_time.python import PythonCodeRunTime, PythonValidator
from prompts.generate_python import EDAFunctionPromptTemplateCreator
from langchain.llms import OpenAI
import json
import plotly.express as px



iris = px.data.iris()

libraries ="""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
"""
tables = """
- variable_name: iris
    discription: Iris Data
    columns: ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'species', 'species_id']
    rows: 150, columns: 6
"""

prompt_creator = EDAFunctionPromptTemplateCreator(libraries, tables)
run_time = PythonCodeRunTime(
    imports=libraries,
    variables={'iris': iris},
    validator=PythonValidator()
)

# Read the Open AI API key from the secret file
with open("secret") as f:
    secret = json.load(f)
    open_ai_key = secret["open_ai_key"]

my_llm = OpenAI(model='text-davinci-003',
    streaming=True, 
    temperature=0.9, 
    openai_api_key=open_ai_key)
llm_conversation = LLMConversation(my_llm,
                                prompt_template_creator=prompt_creator,
                                run_time=run_time,
                                )

llm_conversation.view()
