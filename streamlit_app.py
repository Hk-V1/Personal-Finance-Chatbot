import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

from intent_classifier import IntentClassifier
from budget_advisor import BudgetAdvisor
from chatbot.bot import FinanceChatbot

st.set_page_config(
    page_title="Personal Finance Chatbot",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'chatbot' not in st.session_state:
    st.session_state.chatbot = FinanceChatbot()
if 'messages' not in st.session_state:
    st.session_state.messages = []

def main():
    st.title("Personal Finance Chatbot")
    st.markdown("*AI-powered expense tracking and budget advice*")
    
    with st.sidebar:
        st.header("Dashboard")
        
        summary = st.session_state.chatbot.advisor.get_monthly_summary()
        budget_status = st.session_state.chatbot.advisor.get_budget_status()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Spent", f"${summary['total']:.2f}")
        with col2:
            st.metric("Transactions", summary['transaction_count'])
        
        overall_status = budget_status.get('overall', {})
        if overall_status:
            remaining = overall_status.get('remaining', 0)
            percentage = overall_status.get('percentage_used', 0)
            
            st.metric(
                "Budget Remaining", 
                f"${remaining:.2f}",
                delta=f"{percentage:.1f}% used"
            )
        
        st.header("Quick Actions")
        if st.button("Get Budget Advice"):
            advice = st.session_state.chatbot.advisor.get_spending_advice()
            for tip in advice:
                st.info(tip)
        
        if st.button("Show Budget Status"):
            response = st.session_state.chatbot.process_message("show my budget")
            st.text_area("Budget Status", response, height=200)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Chat with your Finance Assistant")
        
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                if message['type'] == 'user':
                    st.chat_message("user").write(message['content'])
                else:
                    st.chat_message("assistant").write(message['content'])
        
        user_input = st.chat_input("Type your message here... (e.g., 'I spent $50 on groceries')")
        
        if user_input:
            st.session_state.messages.append({
                'type': 'user',
                'content': user_input,
                'timestamp': datetime.now()
            })
            
            bot_response = st.session_state.chatbot.process_message(user_input)
            
            st.session_state.messages.append({
                'type': 'bot',
                'content': bot_response,
                'timestamp': datetime.now()
            })
            
            st.rerun()
    
    with col2:
        st.header("Visualizations")
        
        summary = st.session_state.chatbot.advisor.get_monthly_summary()
        if summary['by_category']:
            df_cat = pd.DataFrame(list(summary['by_category'].items()), 
                                columns=['Category', 'Amount'])
            
            fig_pie = px.pie(df_cat, values='Amount', names='Category', 
                           title="Spending by Category")
            st.plotly_chart(fig_pie, use_container_width=True)
            
            budget_data = []
            for category, budget_amount in st.session_state.chatbot.advisor.budgets.items():
                spent = summary['by_category'].get(category, 0)
                budget_data.append({
                    'Category': category,
                    'Budget': budget_amount,
                    'Spent': spent,
                    'Remaining': budget_amount - spent
                })
            
            df_budget = pd.DataFrame(budget_data)
            
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(name='Budget', x=df_budget['Category'], y=df_budget['Budget']))
            fig_bar.add_trace(go.Bar(name='Spent', x=df_budget['Category'], y=df_budget['Spent']))
            fig_bar.update_layout(title="Budget vs Actual Spending", barmode='group')
            st.plotly_chart(fig_bar, use_container_width=True)
    
    st.header("Recent Transactions")
    expenses_df = st.session_state.chatbot.advisor.get_expenses_df()
    if not expenses_df.empty:
        recent_df = expenses_df.tail(10)[['date', 'description', 'category', 'amount']].copy()
        recent_df['date'] = recent_df['date'].dt.strftime('%Y-%m-%d %H:%M')
        recent_df = recent_df.sort_values('date', ascending=False)
        st.dataframe(recent_df, use_container_width=True)
    else:
        st.info("No transactions yet. Start by adding some expenses through the chat!")
    
    st.header("Try these examples:")
    examples = [
        "I spent $25 on lunch at a restaurant",
        "Add $150 for groceries", 
        "Show my budget breakdown",
        "Give me budget advice",
        "Set my food budget to $600",
        "What's my biggest spending category?"
    ]
    
    cols = st.columns(3)
    for i, example in enumerate(examples):
        with cols[i % 3]:
            if st.button(example, key=f"example_{i}"):
                st.session_state.messages.append({
                    'type': 'user',
                    'content': example,
                    'timestamp': datetime.now()
                })
                
                bot_response = st.session_state.chatbot.process_message(example)
                
                st.session_state.messages.append({
                    'type': 'bot',
                    'content': bot_response,
                    'timestamp': datetime.now()
                })
                
                st.rerun()

if __name__ == "__main__":
    main()
