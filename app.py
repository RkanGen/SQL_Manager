from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import time

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Constants
SUPPORTED_VISUALIZATIONS = ['bar', 'line', 'scatter', 'pie']
MAX_RETRIES = 3
RETRY_DELAY = 2

class DatabaseManager:
    def __init__(self):
        self.db = None
        
    def init_database(self, db_user: str, db_password: str, db_host: str, db_name: str) -> SQLDatabase:
        try:
            connection_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
            self.db = SQLDatabase.from_uri(connection_string)
            return self.db
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {str(e)}")
    
    def get_schema(self):
        if not self.db:
            raise ValueError("Database not initialized")
        return self.db.get_table_info()
    
    def execute_query(self, query: str):
        if not self.db:
            raise ValueError("Database not initialized")
        return self.db.run(query)

class QueryGenerator:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        
    def get_sql_chain(self, schema, chat_history, question):
        template = """
        You are an expert in creating MySQL-compatible SQL queries!
        Always ensure the SQL command uses proper MySQL syntax.
        Based on the table schema below, write a MySQL SQL query that answers the user's question.
        Ensure:
        1. Identifiers like table and column names are enclosed in backticks (`) if needed.
        2. Avoid unnecessary keywords or decorations.

        Schema: {schema}

        Conversation History: {chat_history}

        Generate only the SQL query. Do not include any extra text, comments, or decorators.

        Question: {question}
    """   
        return template.format(schema=schema, chat_history=chat_history, question=question)

    def get_visualization_recommendation(self, sql_result):
        prompt = """
        Analyze the SQL result and recommend the best visualization type.
        Choose from: bar, line, scatter, pie
        Also suggest which columns should be used for x and y axes.
        
        Data:
        {data}
        
        Return response in JSON format:
        {{"viz_type": "", "x_column": "", "y_column": "", "title": ""}}
        """.format(data=sql_result)
        
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except:
            return None

    def generate_natural_language_response(self, sql_query, schema, sql_response):
        prompt = """
        As a data analyst, provide a comprehensive analysis of the SQL query results:
        
        1. Summarize the main findings
        2. Highlight key metrics
        3. Identify any trends or patterns
        4. Provide business insights
        5. Suggest follow-up questions
        
        SQL Query: {sql_query}
        Schema: {schema}
        Results: {sql_response}
        
        Response:
        """.format(sql_query=sql_query, schema=schema, sql_response=sql_response)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"

class DataVisualizer:
    @staticmethod
    def create_visualization(data, viz_config):
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)
            
        viz_type = viz_config.get('viz_type', 'bar')
        x_col = viz_config.get('x_column')
        y_col = viz_config.get('y_column')
        title = viz_config.get('title', 'Data Visualization')
        
        if viz_type == 'bar':
            fig = px.bar(data, x=x_col, y=y_col, title=title)
        elif viz_type == 'line':
            fig = px.line(data, x=x_col, y=y_col, title=title)
        elif viz_type == 'scatter':
            fig = px.scatter(data, x=x_col, y=y_col, title=title)
        elif viz_type == 'pie':
            fig = px.pie(data, values=y_col, names=x_col, title=title)
        
        return fig

def initialize_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="👋 Hello! I'm your SQL Assistant. I can help you query your database, analyze data, and create visualizations. How can I help you today?"),
        ]
    if "db_manager" not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
    if "query_generator" not in st.session_state:
        st.session_state.query_generator = QueryGenerator()

def create_sidebar():
    with st.sidebar:
        st.subheader("📊 Database Connection")
        
        # Connection settings with better defaults and validation
        host = st.text_input("Host", value="localhost", key="host")
        user = st.text_input("User", key="user")
        password = st.text_input("Password", type="password", key="password")
        database = st.text_input("Database", key="database")
        
        if st.button("Connect", key="connect_button"):
            try:
                with st.spinner("🔄 Connecting to database..."):
                    db = st.session_state.db_manager.init_database(user, password, host, database)
                    st.session_state.db = db
                    st.success("✅ Connected successfully!")
                    
                    # Display database info
                    st.subheader("📑 Database Info")
                    schema = st.session_state.db_manager.get_schema()
                    st.code(schema, language="sql")
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")
        
        # Add settings section
        st.subheader("⚙️ Settings")
        st.checkbox("Enable visualizations", value=True, key="enable_viz")
        st.checkbox("Show SQL queries", value=False, key="show_sql")

def main():
    st.set_page_config(
        page_title="Enhanced SQL Assistant",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Enhanced SQL Assistant")
    
    initialize_session_state()
    create_sidebar()
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message("ai" if isinstance(message, AIMessage) else "human"):
            st.markdown(message.content)
    
    # Handle user input
    user_query = st.chat_input("Ask a question about your data...")
    
    if user_query and "db" in st.session_state:
        # Add user message to history
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        with st.chat_message("human"):
            st.markdown(user_query)
            
        with st.chat_message("ai"):
            try:
                with st.spinner("🤔 Thinking..."):
                    # Generate and execute SQL query
                    schema = st.session_state.db_manager.get_schema()
                    prompt = st.session_state.query_generator.get_sql_chain(
                        schema, 
                        st.session_state.chat_history, 
                        user_query
                    )
                    sql_query = st.session_state.query_generator.model.generate_content(prompt).text
                    
                    if st.session_state.show_sql:
                        st.code(sql_query, language="sql")
                    
                    # Execute query with retry logic
                    for attempt in range(MAX_RETRIES):
                        try:
                            sql_response = st.session_state.db_manager.execute_query(sql_query)
                            break
                        except Exception as e:
                            if attempt == MAX_RETRIES - 1:
                                raise e
                            time.sleep(RETRY_DELAY)
                    
                    # Generate natural language response
                    response = st.session_state.query_generator.generate_natural_language_response(
                        sql_query, 
                        schema, 
                        sql_response
                    )
                    st.markdown(response)
                    
                    # Create visualization if enabled
                    if st.session_state.enable_viz and isinstance(sql_response, (list, dict)):
                        viz_config = st.session_state.query_generator.get_visualization_recommendation(sql_response)
                        if viz_config:
                            fig = DataVisualizer.create_visualization(sql_response, viz_config)
                            st.plotly_chart(fig)
                    
                    # Add response to chat history
                    st.session_state.chat_history.append(AIMessage(content=response))
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.chat_history.append(AIMessage(content=f"I encountered an error: {str(e)}"))

if __name__ == "__main__":
    main()
