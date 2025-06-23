import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import random
from chatbot import FinanceChatbot
from intent_classifier import IntentClassifier
from budget_advisor import BudgetAdvisor

st.markdown("""
<style>
    /* Import a more personal font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Caveat:wght@400;600&display=swap');
    
    /* Overall app styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Custom header with personality */
    .finance-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
    }
    
    .finance-header h1 {
        color: white;
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .finance-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin: 0;
        font-weight: 400;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Chat message styling */
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .stChatMessage[data-testid="chat-message-user"] {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] {
        background: white;
        border: 1px solid #e2e8f0;
    }
    
    /* Metric cards with personality */
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 4px solid #10b981;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    
    .metric-card.warning {
        border-left-color: #f59e0b;
    }
    
    .metric-card.danger {
        border-left-color: #ef4444;
    }
    
    /* Button improvements */
    .stButton > button {
        border-radius: 8px;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 500;
        transition: all 0.2s ease;
        padding: 0.6rem 1.2rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Example button styling */
    .example-btn {
        background: white !important;
        color: #4f46e5 !important;
        border: 2px solid #4f46e5 !important;
        margin: 0.25rem;
        font-size: 0.9rem;
    }
    
    .example-btn:hover {
        background: #4f46e5 !important;
        color: white !important;
    }
    
    /* Chart containers */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }
    
    /* Transactions table */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Fun loading messages */
    .loading-message {
        font-family: 'Caveat', cursive;
        font-size: 1.2rem;
        color: #6b7280;
        text-align: center;
        padding: 2rem;
    }
    
    /* Advice cards */
    .advice-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #f59e0b;
    }
    
    /* Custom icons */
    .status-icon {
        font-size: 1.2rem;
        margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

MOTIVATIONAL_MESSAGES = [
    "Every penny counts! 💪",
    "Building wealth one transaction at a time",
    "Smart spending = future freedom",
    "Your financial future self will thank you",
    "Small steps, big financial wins!"
]

LOADING_MESSAGES = [
    "Crunching your numbers... 🤓",
    "Analyzing your spending patterns...",
    "Calculating your financial awesomeness...",
    "Putting on our accountant hat...",
    "Digging through your expense receipts..."
]

st.set_page_config(
    page_title="MoneyWise - Your Personal Finance Buddy",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'chatbot' not in st.session_state:
    st.session_state.chatbot = FinanceChatbot()
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

def get_status_color_and_icon(status):
    """Human touch: meaningful visual feedback"""
    if status == "over_budget":
        return "🚨", "#ef4444", "danger"
    elif status == "warning":
        return "⚠️", "#f59e0b", "warning"
    else:
        return "✅", "#10b981", "good"

def format_currency_human(amount):
    """Human touch: friendly currency formatting"""
    if amount >= 1000:
        return f"${amount:,.0f}"
    else:
        return f"${amount:.2f}"

def get_personal_greeting():
    """Human touch: time-aware greetings"""
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning! ☀️"
    elif hour < 17:
        return "Good afternoon! 🌤️"
    else:
        return "Good evening! 🌙"

st.markdown(f"""
<div class="finance-header">
    <h1>💰 MoneyWise</h1>
    <p>{get_personal_greeting()} Ready to make some smart money moves?</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📊 Your Money Dashboard")
    
    summary = st.session_state.chatbot.advisor.get_monthly_summary()
    budget_status = st.session_state.chatbot.advisor.get_budget_status()
    overall_status = budget_status.get('overall', {})
    
    if not st.session_state.user_name:
        name = st.text_input("What should I call you?", placeholder="Your name here...")
        if name:
            st.session_state.user_name = name
            st.success(f"Nice to meet you, {name}! 👋")
    else:
        st.markdown(f"**Hey there, {st.session_state.user_name}!** 👋")
    
    if overall_status:
        icon, color, card_class = get_status_color_and_icon(overall_status.get('status', 'good'))
        
        st.markdown(f"""
        <div class="metric-card {card_class}">
            <div style="display: flex; align-items: center;">
                <span class="status-icon">{icon}</span>
                <div>
                    <strong>Budget Health</strong><br>
                    <span style="color: {color}; font-size: 1.5rem; font-weight: bold;">
                        {format_currency_human(overall_status.get('remaining', 0))}
                    </span> left this month
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "This Month", 
            format_currency_human(summary['total']),
            delta=f"{summary['transaction_count']} purchases"
        )
    with col2:
        if summary['transaction_count'] > 0:
            avg = summary['average_transaction']
            st.metric(
                "Avg Purchase", 
                format_currency_human(avg),
                delta="per transaction"
            )
    
    if summary['total'] > 0:
        st.info(f"💡 {random.choice(MOTIVATIONAL_MESSAGES)}")
    
    st.markdown("---")
    
    st.markdown("### ⚡ Quick Actions")
    
    if st.button("📈 Get Smart Advice", use_container_width=True):
        with st.spinner(random.choice(LOADING_MESSAGES)):
            advice = st.session_state.chatbot.advisor.get_spending_advice()
            for tip in advice:
                st.markdown(f'<div class="advice-card">💡 {tip}</div>', unsafe_allow_html=True)
    
    if st.button("📋 Show Budget Breakdown", use_container_width=True):
        response = st.session_state.chatbot.process_message("show my budget")
        st.code(response, language=None)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 💬 Chat with MoneyWise")
    
    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; color: #6b7280;">
                <h4>👋 Hey there! I'm MoneyWise, your friendly finance buddy.</h4>
                <p>I'm here to help you track expenses, manage budgets, and make smarter money decisions. 
                Try saying something like "I spent $25 on lunch" or click the examples below!</p>
            </div>
            """, unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            if message['type'] == 'user':
                st.chat_message("user").write(message['content'])
            else:
                st.chat_message("assistant").write(message['content'])
    
    user_input = st.chat_input("💭 Tell me about your spending... (e.g., 'I bought coffee for $4.50')")

with col2:
    st.markdown("### 📈 Visual Insights")
    
    summary = st.session_state.chatbot.advisor.get_monthly_summary()
    
    if summary['by_category']:
        df_cat = pd.DataFrame(list(summary['by_category'].items()), 
                            columns=['Category', 'Amount'])
        
        category_names = {
            'food_dining': '🍕 Food & Dining',
            'transportation': '🚗 Transportation', 
            'shopping': '🛍️ Shopping',
            'entertainment': '🎬 Entertainment',
            'utilities_bills': '⚡ Bills & Utilities',
            'healthcare': '🏥 Healthcare',
            'education': '📚 Education',
            'travel': '✈️ Travel',
            'other': '📦 Other'
        }
        
        df_cat['Category'] = df_cat['Category'].map(category_names).fillna(df_cat['Category'])
        
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        fig_pie = px.pie(df_cat, values='Amount', names='Category', 
                       title="Where Your Money Goes",
                       color_discrete_sequence=px.colors.qualitative.Set3)
        fig_pie.update_layout(
            font=dict(family="Inter, sans-serif", size=12),
            title_font_size=16,
            showlegend=True
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        budget_data = []
        for category, budget_amount in st.session_state.chatbot.advisor.budgets.items():
            spent = summary['by_category'].get(category, 0)
            pretty_name = category_names.get(category, category)
            budget_data.append({
                'Category': pretty_name,
                'Budget': budget_amount,
                'Spent': spent,
                'Remaining': max(0, budget_amount - spent)
            })
        
        df_budget = pd.DataFrame(budget_data)
        
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name='💰 Budget', 
            x=df_budget['Category'], 
            y=df_budget['Budget'],
            marker_color='rgba(102, 126, 234, 0.7)'
        ))
        fig_bar.add_trace(go.Bar(
            name='💸 Spent', 
            x=df_budget['Category'], 
            y=df_budget['Spent'],
            marker_color='rgba(239, 68, 68, 0.8)'
        ))
        fig_bar.update_layout(
            title="Budget vs Reality Check",
            barmode='group',
            font=dict(family="Inter, sans-serif"),
            title_font_size=16,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="loading-message">
            📊 Your spending insights will appear here once you start tracking expenses!
        </div>
        """, unsafe_allow_html=True)

st.markdown("### 📋 Recent Activity")
expenses_df = st.session_state.chatbot.advisor.get_expenses_df()
if not expenses_df.empty:
    recent_df = expenses_df.tail(10)[['date', 'description', 'category', 'amount']].copy()
    recent_df['date'] = recent_df['date'].dt.strftime('%m/%d %H:%M')
    
    recent_df.columns = ['Date', 'What you bought', 'Category', 'Amount']
    recent_df['Amount'] = recent_df['Amount'].apply(lambda x: f"${x:.2f}")
    recent_df = recent_df.sort_values('Date', ascending=False)
    
    st.dataframe(
        recent_df, 
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("🎯 No transactions yet. Let's start tracking your spending journey!")

st.markdown("### 💡 Not sure what to say? Try these:")

examples = [
    "🍕 I spent $25 on pizza delivery",
    "☕ Bought coffee for $4.50", 
    "📊 How's my budget looking?",
    "💰 Give me some money advice",
    "🛍️ Set my shopping budget to $400",
    "📈 What's my biggest expense?"
]

cols = st.columns(2)
for i, example in enumerate(examples):
    with cols[i % 2]:
        if st.button(example, key=f"example_{i}", use_container_width=True):
            # Add to messages
            st.session_state.messages.append({
                'type': 'user',
                'content': example.split(' ', 1)[1],  # Remove emoji from actual message
                'timestamp': datetime.now()
            })
            
            bot_response = st.session_state.chatbot.process_message(example.split(' ', 1)[1])
            
            st.session_state.messages.append({
                'type': 'bot',
                'content': bot_response,
                'timestamp': datetime.now()
            })
            
            st.rerun()

if user_input:
    st.session_state.messages.append({
        'type': 'user',
        'content': user_input,
        'timestamp': datetime.now()
    })

    with st.spinner("💭 Thinking..."):
        bot_response = st.session_state.chatbot.process_message(user_input)

    st.session_state.messages.append({
        'type': 'bot',
        'content': bot_response,
        'timestamp': datetime.now()
    })

    st.rerun()

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; padding: 1rem;">
    <small>💜 Made with care to help you build better money habits • MoneyWise v1.0</small>
</div>
""", unsafe_allow_html=True)
