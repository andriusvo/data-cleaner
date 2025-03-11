import streamlit as st
import tools as agent_tools
from langchain.chat_models import ChatOpenAI, ChatAnthropic
from langchain_mistralai.chat_models import ChatMistralAI
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate

def get_llm(provider):
    if provider == "OpenAI":
        return ChatOpenAI(temperature=0, model="gpt-4o", api_key=st.secrets["OPENAI_API_KEY"])
    elif provider == "Anthropic":
        return ChatAnthropic(temperature=0, model="claude-3-5-sonnet-20240620", anthropic_api_key=st.secrets["ANTHROPIC_API_KEY"])
    elif provider == "Mistral":
        return ChatMistralAI(temperature=0, model="mistral-large-latest", mistral_api_key=st.secrets["MISTRAL_API_KEY"])
    else:
        raise ValueError("Unsupported LLM provider.")

class DataCleanerAgent:
    def __init__(self, provider, df, missing_values_strategy):
        llm = get_llm(provider)
        
        tools = [
            Tool(
                name="detect_missing_values",
                func=lambda _: agent_tools.detect_missing_values(df).to_markdown(),
                description="Detects missing values in the dataset and provides statistics. No input is needed.",
            ),
            Tool(
                name="drop_missing_values",
                func=lambda x: "Operation completed. Use the 'get_dataframe_info' tool to see the current state.",
                description="Drops rows with missing values. Input can be a comma-separated list of column names, or leave empty to drop rows with any missing values.",
            ),
            Tool(
                name="fill_missing_with_mean",
                func=lambda x: "Operation completed. Use the 'get_dataframe_info' tool to see the current state.",
                description="Fills missing values with the column mean for numeric columns. Input can be a comma-separated list of column names, or leave empty to fill all numeric columns.",
            ),
            Tool(
                name="detect_outliers",
                func=lambda x: agent_tools.detect_outliers(df, threshold=float(x) if x and x.strip() and x != "_" and x.lower() != "none" else 3).to_markdown(),
                description="Detects outliers in numeric columns using Z-Score method. Input is the Z-Score threshold (default 3).",
            ),
            Tool(
                name="remove_outliers",
                func=lambda x: "Operation completed. Use the 'get_dataframe_info' tool to see the current state.",
                description="Removes outliers from numeric columns using Z-Score method. Input format: 'threshold,col1,col2,...' or just 'threshold' to check all numeric columns. Default threshold is 3.",
            ),
            Tool(
                name="remove_duplicates",
                func=lambda x: "Operation completed. Use the 'get_dataframe_info' tool to see the current state.",
                description="Removes duplicate rows. Input can be a comma-separated list of column names to consider for duplicates, or leave empty to check all columns.",
            ),
            Tool(
                name="get_dataframe_info",
                func=lambda _: f"DataFrame shape: {df.shape}\nColumns: {', '.join(df.columns.tolist())}\nDatatypes:\n{df.dtypes.to_string()}",
                description="Returns information about the current state of the dataframe. No input is needed.",
            ),
            Tool(
                name="get_dataframe_sample",
                func=lambda x: df.head(int(x) if x and x.strip() and x.strip().isdigit() else 5).to_markdown(),
                description="Returns a sample of the first N rows of the dataframe. Input is the number of rows to show (default 5).",
            )
        ]

        if missing_values_strategy == "fill_mean":
            missing_values_instruction = "3. Handle missing values - use fill_missing_with_mean for numeric columns"
        else:
            missing_values_instruction = "3. Handle missing values - use drop_missing_values to remove rows with missing values"
        
        prompt = PromptTemplate.from_template(f"""
        You are a data cleaning assistant. Follow these instructions to clean the dataset:
        
        1. Start by understanding the dataset structure using get_dataframe_info and get_dataframe_sample
        2. Check for missing values with detect_missing_values
        {missing_values_instruction}
        4. Check for outliers with detect_outliers
        5. Remove outliers with remove_outliers if necessary
        6. Remove duplicates with remove_duplicates
        7. Provide a detailed summary of all issues found and actions taken
        
        You have access to the following tools:

        {{tools}}

        Use the following format:

        Thought: you should always think about what to do
        Action: the action to take, should be one of [{{tool_names}}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: Provide a summary of all the cleaning steps taken and the final state of the data

        Question: Analyze this dataset and perform comprehensive cleaning to handle missing values, outliers, and duplicates automatically. Be thorough and explain what cleaning steps were taken.
        {{agent_scratchpad}}
        """)
        
        react_agent = create_react_agent(llm, tools, prompt)
        
        self.agent = AgentExecutor(
            agent=react_agent,
            tools=tools,
            verbose=True,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
            max_execution_time=60,
            max_iterations=60
        )
