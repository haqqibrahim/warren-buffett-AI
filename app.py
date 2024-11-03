import os
import datetime
import streamlit as st
from typing import TypedDict, Annotated, Sequence, List, Optional, Union, Dict, Literal
import operator
from enum import Enum

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain.tools.render import format_tool_to_openai_function
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, StateGraph, MessagesState
from langchain_community.tools import IncomeStatements, BalanceSheets, CashFlowStatements
from langchain_community.utilities.financial_datasets import FinancialDatasetsAPIWrapper
import requests

# Set up page config
st.set_page_config(page_title="Warren Buffett AI Agent", layout="wide")

# Access secrets
if not st.secrets["GOOGLE_API_KEY"]:
    st.error("Missing GOOGLE_API_KEY in secrets")
    st.stop()
    
if not st.secrets["FINANCIAL_DATASETS_API_KEY"]:
    st.error("Missing FINANCIAL_DATASETS_API_KEY in secrets") 
    st.stop()
    
if not st.secrets["TAVILY_API_KEY"]:
    st.error("Missing TAVILY_API_KEY in secrets")
    st.stop()

# Set environment variables from secrets
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
os.environ["FINANCIAL_DATASETS_API_KEY"] = st.secrets["FINANCIAL_DATASETS_API_KEY"] 
os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]

# Tool definitions
@tool
def roe(net_income: float, equity: float) -> float:
    """Computes the return on equity (ROE) for a given company."""
    return net_income / equity

@tool 
def roic(
    operating_income: float,
    total_debt: float,
    equity: float,
    cash_and_equivalents: float,
    tax_rate: float = 0.35,
) -> float:
    """Computes the return on invested capital (ROIC)."""
    net_operating_profit_after_tax = operating_income * (1 - tax_rate)
    invested_capital = total_debt + equity - cash_and_equivalents
    return net_operating_profit_after_tax / invested_capital

@tool
def owner_earnings(
    net_income: float,
    depreciation_amortization: float = 0.0,
    capital_expenditures: float = 0.0
):
    """Calculates the owner earnings."""
    return net_income + depreciation_amortization - capital_expenditures

@tool
def intrinsic_value(
    free_cash_flow: float,
    growth_rate: float = 0.05,
    discount_rate: float = 0.10,
    terminal_growth_rate: float = 0.02,
    num_years: int = 5,
) -> float:
    """Computes the discounted cash flow (DCF)."""
    cash_flows = [free_cash_flow * (1 + growth_rate) ** i for i in range(num_years)]
    present_values = []
    for i in range(num_years):
        present_value = cash_flows[i] / (1 + discount_rate) ** (i + 1)
        present_values.append(present_value)
    terminal_value = cash_flows[-1] * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)
    terminal_present_value = terminal_value / (1 + discount_rate) ** num_years
    return sum(present_values) + terminal_present_value

@tool
def percentage_change(start: float, end: float):
    """Calculate percentage change between two values."""
    if start == 0:
        raise ValueError("Start cannot be zero")
    return round(((end - start) / start) * 100, 2)

# Create the Warren Buffett AI Agent
def create_agent():
    # Create the tools
    api_wrapper = FinancialDatasetsAPIWrapper()
    integration_tools = [
        IncomeStatements(api_wrapper=api_wrapper),
        BalanceSheets(api_wrapper=api_wrapper),
        CashFlowStatements(api_wrapper=api_wrapper),
    ]

    local_tools = [intrinsic_value, roe, roic, owner_earnings, percentage_change]
    tools = integration_tools + local_tools

    tool_node = ToolNode(tools)

    # Set up the model
    google_model = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro", 
        temperature=0
    ).bind_tools(tools)

    # System prompt
    system_prompt = f"""
    You are an AI financial agent with expertise in analyzing businesses using methods similar to those of Warren Buffett. 
    Your task is to provide short, accurate, and concise answers to questions about company financials and performance.

    You use financial tools to answer the questions. The tools give you access to data sources like income statements, stock prices, etc.

    When answering questions:
    1. Focus on providing accurate financial data and insights.
    2. Use specific numbers and percentages when available.
    3. Make comparisons between different time periods if relevant.
    4. Keep your answers short, concise, and to the point.

    Important: You must be short and concise with your answers.

    The current date is {datetime.date.today().strftime("%Y-%m-%d")}
    """

    # Define the function that determines whether to continue or not
    def should_continue(state: MessagesState) -> Literal["tools", END]:
        messages = state['messages']
        last_message = messages[-1]
        return "tools" if last_message.tool_calls else END

    # Define the function that calls the model
    def call_agent(state: MessagesState):
        prompt = SystemMessage(content=system_prompt)
        messages = state['messages']
        if messages and messages[0].content != system_prompt:
            messages.insert(0, prompt)
        return {"messages": [google_model.invoke(messages)]}

    def call_output(state: MessagesState):
        prompt = SystemMessage(content=system_prompt)
        messages = state['messages']
        if messages and messages[0].content != system_prompt:
            messages.insert(0, prompt)
        return {"messages": [google_model.invoke(messages)]}

    # Define the graph
    workflow = StateGraph(MessagesState)
    workflow.add_node("agent", call_agent)
    workflow.add_node("tools", tool_node)
    workflow.add_node("output", call_output)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", END: END}
    )
    workflow.add_edge("tools", "output")

    return workflow.compile()

# Streamlit UI
def main():
    st.title("Warren Buffett AI Financial Advisor 💰")
    st.markdown("""
    This AI agent analyzes stocks and provides financial insights using Warren Buffett's investment principles.
    
    **Disclaimer**: This is not financial advice. Do your own due diligence.
    """)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create the agent
    agent = create_agent()

    # Chat input
    if prompt := st.chat_input("Ask about a stock (e.g., What is AAPL's revenue?)"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = agent.invoke(
                    {"messages": [HumanMessage(content=prompt)]},
                    config={"configurable": {"thread_id": 42}}
                )
                ai_response = response["messages"][-1].content
                st.markdown(ai_response)
                
        # Add AI response to chat history
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

if __name__ == "__main__":
    main()
