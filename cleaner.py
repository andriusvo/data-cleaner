import streamlit as st
import pandas as pd
import tools as agent_tools
import utils
from agent import DataCleanerAgent

st.set_page_config(page_title="Automated Data Cleaning", layout="wide")

if 'df' not in st.session_state:
    st.session_state.df = None
if 'cleaned_df' not in st.session_state:
    st.session_state.cleaned_df = None
if 'report' not in st.session_state:
    st.session_state.report = []
if 'original_file_type' not in st.session_state:
    st.session_state.original_file_type = None
if 'agent_response' not in st.session_state:
    st.session_state.agent_response = None
if 'cleaning_completed' not in st.session_state:
    st.session_state.cleaning_completed = False
if 'missing_values_strategy' not in st.session_state:
    st.session_state.missing_values_strategy = "fill_mean"
if 'ai_provider' not in st.session_state:
    st.session_state.ai_provider = "OpenAI"

def process_agent_steps(steps, missing_values_strategy):
    df = st.session_state.df.copy()
    
    for step in steps:
        tool_name = step[0].tool
        tool_input = step[0].tool_input
        
        if tool_name == "drop_missing_values" and missing_values_strategy == "drop":
            if tool_input and tool_input.strip() and tool_input != "_":
                columns = [col.strip() for col in tool_input.split(",") if col.strip()]
            else:
                columns = None
            df = agent_tools.drop_missing_values(df, columns)
        
        elif tool_name == "fill_missing_with_mean" and missing_values_strategy == "fill_mean":
            if tool_input and tool_input.strip() and tool_input != "_":
                columns = [col.strip() for col in tool_input.split(",") if col.strip()]
            else:
                columns = None
            df = agent_tools.fill_missing_with_mean(df, columns)
        
        elif tool_name == "remove_outliers":
            if not tool_input or tool_input.strip() == "" or tool_input == "_":
                threshold = 3
                columns = None
            else:
                parts = [p.strip() for p in tool_input.split(",") if p.strip()]
                try:
                    threshold = float(parts[0]) if parts and parts[0] else 3
                except ValueError:
                    threshold = 3
                columns = parts[1:] if len(parts) > 1 else None
            df = agent_tools.remove_outliers(df, columns, threshold)
        
        elif tool_name == "remove_duplicates":
            if tool_input and tool_input.strip() and tool_input != "_":
                subset = [col.strip() for col in tool_input.split(",") if col.strip()]
            else:
                subset = None
            df = agent_tools.remove_duplicates(df, subset)
    
    return df

def run_automated_cleaning():
    cleaning_agent = DataCleanerAgent(st.session_state.ai_provider, st.session_state.df, st.session_state.missing_values_strategy)
    
    with st.spinner(f"AI is analyzing and cleaning your dataset..."):
        st.session_state.report = []
        
        response = cleaning_agent.agent.invoke({
            "input": "Analyze this dataset and perform comprehensive cleaning to handle missing values, outliers, and duplicates automatically."
        })
        
        st.session_state.cleaned_df = process_agent_steps(response["intermediate_steps"], st.session_state.missing_values_strategy)
        st.session_state.agent_response = response["output"]
        st.session_state.cleaning_completed = True
    
    return True

st.title("Automated Data Cleaning")
st.write("Upload a CSV or Excel file and let AI clean your dataset automatically.")

uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            st.session_state.original_file_type = ".csv"
        else:
            df = pd.read_excel(uploaded_file)
            st.session_state.original_file_type = "." + uploaded_file.name.split(".")[-1].lower()
        
        st.session_state.df = df
        st.session_state.cleaned_df = df.copy()
        st.session_state.report = []
        st.session_state.cleaning_completed = False
        st.session_state.agent_response = None
    except Exception as e:
        st.error(f"Error reading the file: {e}")

if st.session_state.df is not None:
    tab1, tab2, tab3 = st.tabs(["Dataset", "AI Cleaning", "Results"])

    with tab1:
        st.subheader("Original Dataset")
        st.dataframe(st.session_state.df, use_container_width=True)
    
    with tab2:
        st.subheader("AI Data Cleaning")
        st.write("Let the AI analyze your dataset and clean it automatically.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.missing_values_strategy = st.radio(
                "How would you like to handle missing values?",
                options=["fill_mean", "drop"],
                format_func=lambda x: "Fill with mean (for numeric columns)" if x == "fill_mean" else "Drop rows with missing values",
                index=0 if st.session_state.missing_values_strategy == "fill_mean" else 1
            )
        
        with col2:
            st.session_state.ai_provider = st.selectbox(
                "Choose AI Provider",
                options=["OpenAI", "Mistral", "Anthropic"],
                index=["OpenAI", "Mistral", "Anthropic"].index(st.session_state.ai_provider)
            )
        
        if st.button("Process Dataset"):
            success = run_automated_cleaning()
            if success:
                st.success("Dataset cleaning completed!")
        
        if st.session_state.agent_response:
            st.subheader("AI Analysis")
            st.write(st.session_state.agent_response)
    
    with tab3:
        st.subheader("Results")
        
        if st.session_state.cleaning_completed:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("Original Dataset")
                st.write(f"Rows: {st.session_state.df.shape[0]}")
                st.write(f"Columns: {st.session_state.df.shape[1]}")
            
            with col2:
                st.write("Cleaned Dataset")
                st.write(f"Rows: {st.session_state.cleaned_df.shape[0]}")
                st.write(f"Columns: {st.session_state.cleaned_df.shape[1]}")
            
            st.subheader("Cleaned Dataset")
            st.dataframe(st.session_state.cleaned_df, use_container_width=True)
            
            st.subheader("Cleaning Report")
            if st.session_state.report:
                for item in st.session_state.report:
                    st.write(f"- {item}")
            
            if st.session_state.df.shape != st.session_state.cleaned_df.shape:
                rows_change = st.session_state.df.shape[0] - st.session_state.cleaned_df.shape[0]
                cols_change = st.session_state.df.shape[1] - st.session_state.cleaned_df.shape[1]
                
                if rows_change > 0:
                    st.write(f"- Removed {rows_change} rows ({rows_change/st.session_state.df.shape[0]*100:.1f}%)")
                if cols_change > 0:
                    st.write(f"- Removed {cols_change} columns ({cols_change/st.session_state.df.shape[1]*100:.1f}%)")
            
            st.markdown(
                utils.get_download_link(
                    st.session_state.cleaned_df, 
                    filename=f"cleaned_data{st.session_state.original_file_type}", 
                    original_file_type=st.session_state.original_file_type
                ), 
                unsafe_allow_html=True
            )
        else:
            st.info("Please upload a file and process it in the 'AI Cleaning' tab to see results.")