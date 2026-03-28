"""
Expense Manager App - Main Streamlit Application
Owner: Aryan Chavan
Optimized for performance with caching and efficient rendering.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

# Import custom modules
from database import get_database
from ai_analyzer import get_ai_analyzer

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Expense Manager | Aryan Chavan",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Custom CSS for top navigation and modern styling
st.markdown("""
<style>
    /* Hide default sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Mobile-first responsive design */
    * {
        box-sizing: border-box;
    }
    
    /* Top navigation bar */
    .top-nav {
        display: flex;
        justify-content: center;
        gap: 10px;
        padding: 15px 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Tab styling - responsive */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        padding: 0;
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        color: #333;
        border: none;
        transition: all 0.3s ease;
        min-height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #ffffff;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Card styling - responsive */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 15px;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #666;
        margin-top: 5px;
    }
    
    /* Button styling - touch-friendly */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        min-height: 44px;
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Input styling - mobile-friendly */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        padding: 12px;
        font-size: 16px;
        min-height: 44px;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Chat container - responsive */
    .chat-container {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 15px;
        height: 400px;
        overflow-y: auto;
        -webkit-overflow-scrolling: touch;
    }
    
    /* User message - responsive */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        max-width: 85%;
        margin-left: auto;
        word-wrap: break-word;
    }
    
    /* Assistant message - responsive */
    .assistant-message {
        background-color: #ffffff;
        color: #333;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        max-width: 85%;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        word-wrap: break-word;
    }
    
    /* Header styling - responsive */
    .main-header {
        text-align: center;
        padding: 15px 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 1.8rem;
    }
    
    .main-header p {
        margin: 5px 0 0 0;
        opacity: 0.9;
        font-size: 0.9rem;
    }
    
    /* Expense item - responsive */
    .expense-item {
        background-color: #ffffff;
        padding: 12px;
        border-radius: 10px;
        margin: 8px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #667eea;
    }
    
    /* Success/Error messages */
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
    }
    
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #f5c6cb;
    }
    
    /* Loading spinner */
    .stSpinner {
        text-align: center;
    }
    
    /* Footer - responsive */
    .footer {
        text-align: center;
        padding: 15px;
        color: #666;
        font-size: 0.85rem;
        margin-top: 30px;
    }
    
    /* Mobile-specific styles */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.5rem;
        }
        
        .main-header p {
            font-size: 0.8rem;
        }
        
        .metric-value {
            font-size: 1.2rem;
        }
        
        .metric-label {
            font-size: 0.75rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 8px 12px;
            font-size: 0.85rem;
        }
        
        .chat-container {
            height: 350px;
            padding: 10px;
        }
        
        .user-message, .assistant-message {
            max-width: 90%;
            padding: 10px 12px;
        }
    }
    
    /* Tablet styles */
    @media (min-width: 769px) and (max-width: 1024px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .metric-value {
            font-size: 1.8rem;
        }
    }
    
    /* Desktop styles */
    @media (min-width: 1025px) {
        .main-header h1 {
            font-size: 2.5rem;
        }
        
        .metric-value {
            font-size: 2rem;
        }
        
        .metric-card {
            padding: 20px;
        }
    }
    
    /* iOS-specific fixes */
    @supports (-webkit-touch-callout: none) {
        .stTextInput input, .stNumberInput input {
            font-size: 16px;
        }
    }
    
    /* Android-specific fixes */
    @media screen and (max-width: 768px) {
        .stButton button {
            -webkit-tap-highlight-color: transparent;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize all session state variables."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "Dashboard"

# Authentication functions
def show_login_page():
    """Display login/register page."""
    st.markdown("""
    <div class="main-header">
        <h1>💰 Expense Manager</h1>
        <p>Smart Financial Tracking & AI-Powered Insights</p>
        <p style="font-size: 0.8rem; opacity: 0.8;">Created by Aryan Chavan</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            with st.form("login_form"):
                st.subheader("Welcome Back!")
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submit = st.form_submit_button("Login", use_container_width=True)
                
                if submit:
                    if username and password:
                        db = get_database()
                        if db.authenticate_user(username, password):
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.success("Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                    else:
                        st.warning("Please fill in all fields")
        
        with tab2:
            with st.form("register_form"):
                st.subheader("Create Account")
                new_username = st.text_input("Username", placeholder="Choose a username")
                new_password = st.text_input("Password", type="password", placeholder="Create a password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                submit = st.form_submit_button("Register", use_container_width=True)
                
                if submit:
                    if new_username and new_password and confirm_password:
                        if new_password != confirm_password:
                            st.error("Passwords do not match")
                        elif len(new_password) < 6:
                            st.error("Password must be at least 6 characters")
                        else:
                            db = get_database()
                            if db.create_user(new_username, new_password):
                                st.success("Account created successfully! Please login.")
                            else:
                                st.error("Username already exists")
                    else:
                        st.warning("Please fill in all required fields")

def show_main_app():
    """Display main application with all tabs."""
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>💰 Expense Manager</h1>
        <p>Welcome, {st.session_state.username}! | Smart Financial Tracking</p>
        <p style="font-size: 0.8rem; opacity: 0.8;">Created by Aryan Chavan</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Logout button in top right
    col1, col2, col3 = st.columns([6, 1, 1])
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.chat_history = []
            st.rerun()
    
    # Top navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Dashboard", 
        "➕ Add Expense", 
        "💵 Income", 
        "📈 Analysis", 
        "💡 Budget Advice",
        "🤖 AI Chat"
    ])
    
    with tab1:
        show_dashboard()
    
    with tab2:
        show_add_expense()
    
    with tab3:
        show_income_management()
    
    with tab4:
        show_analysis()
    
    with tab5:
        show_budget_advice()
    
    with tab6:
        show_ai_chat()

def show_dashboard():
    """Display dashboard with expense overview."""
    st.header("📊 Financial Dashboard")
    
    db = get_database()
    username = st.session_state.username
    
    # Get data
    expenses = db.get_user_expenses(username, limit=100)
    income = db.get_income(username)
    summary = db.get_expense_summary(username)
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">₹{summary['total_expenses']:.2f}</div>
            <div class="metric-label">Total Expenses</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">₹{summary['monthly_average']:.2f}</div>
            <div class="metric-label">Monthly Average</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        monthly_income = income['monthly_income'] if income else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">₹{monthly_income:.2f}</div>
            <div class="metric-label">Monthly Income</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        savings = monthly_income - summary['monthly_average'] if monthly_income > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">₹{savings:.2f}</div>
            <div class="metric-label">Monthly Savings</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts with lazy loading
    col1, col2 = st.columns(2)
    
    with col1:
        if summary['category_breakdown']:
            st.subheader("📁 Expenses by Category")
            # Lazy load chart
            with st.spinner("Loading chart..."):
                fig = px.pie(
                    values=list(summary['category_breakdown'].values()),
                    names=list(summary['category_breakdown'].keys()),
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No expense data available for chart")
    
    with col2:
        if expenses:
            st.subheader("📅 Recent Expenses")
            # Lazy load timeline chart
            with st.spinner("Loading timeline..."):
                df = pd.DataFrame(expenses)
                df['date'] = pd.to_datetime(df['date'])
                df_daily = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
                df_daily.columns = ['Date', 'Amount']
                
                fig = px.line(
                    df_daily,
                    x='Date',
                    y='Amount',
                    markers=True,
                    color_discrete_sequence=['#667eea']
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No expense data available for timeline")
    
    # Recent transactions
    st.subheader("🕐 Recent Transactions")
    if expenses:
        for expense in expenses[:10]:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.write(f"**{expense['expense_name']}**")
            with col2:
                st.write(f"📁 {expense.get('category', 'Other')}")
            with col3:
                st.write(f"📅 {expense['date'][:10]}")
            with col4:
                st.write(f"**₹{expense['amount']:.2f}**")
    else:
        st.info("No expenses recorded yet. Add your first expense!")

def show_add_expense():
    """Display add expense form."""
    st.header("➕ Add New Expense")
    
    db = get_database()
    username = st.session_state.username
    
    with st.form("add_expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            expense_name = st.text_input("Expense Name*", placeholder="e.g., Grocery Shopping")
            amount = st.number_input("Amount (₹)*", min_value=0.01, step=0.01, format="%.2f")
        
        with col2:
            category = st.selectbox(
                "Category",
                ["Food & Dining", "Transportation", "Shopping", "Entertainment", 
                 "Bills & Utilities", "Healthcare", "Education", "Travel", "Other"]
            )
            description = st.text_area("Description (Optional)", placeholder="Add notes...")
        
        submit = st.form_submit_button("💾 Add Expense", use_container_width=True)
        
        if submit:
            if expense_name and amount > 0:
                if db.add_expense(username, expense_name, amount, category, description):
                    st.success(f"✅ Expense '{expense_name}' added successfully!")
                    st.balloons()
                else:
                    st.error("Failed to add expense. Please try again.")
            else:
                st.warning("Please fill in all required fields")
    
    # Recent expenses
    st.markdown("---")
    st.subheader("📋 Your Recent Expenses")
    
    expenses = db.get_user_expenses(username, limit=20)
    
    if expenses:
        for expense in expenses:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                with col1:
                    st.write(f"**{expense['expense_name']}**")
                    if expense.get('description'):
                        st.caption(expense['description'])
                with col2:
                    st.write(f"📁 {expense.get('category', 'Other')}")
                with col3:
                    st.write(f"📅 {expense['date'][:10]}")
                with col4:
                    st.write(f"**₹{expense['amount']:.2f}**")
                st.markdown("---")
    else:
        st.info("No expenses recorded yet.")

def show_income_management():
    """Display income management section."""
    st.header("💵 Income Management")
    
    db = get_database()
    username = st.session_state.username
    
    # Get current income
    current_income = db.get_income(username)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("💰 Set Your Income")
        
        with st.form("income_form"):
            monthly_income = st.number_input(
                "Monthly Income (₹)",
                min_value=0.0,
                value=current_income['monthly_income'] if current_income else 0.0,
                step=100.0,
                format="%.2f"
            )
            
            yearly_income = st.number_input(
                "Yearly Income (₹) - Optional",
                min_value=0.0,
                value=current_income['yearly_income'] if current_income else 0.0,
                step=1000.0,
                format="%.2f",
                help="Leave as 0 to auto-calculate (Monthly × 12)"
            )
            
            submit = st.form_submit_button("💾 Save Income", use_container_width=True)
            
            if submit:
                if monthly_income > 0:
                    if db.set_income(username, monthly_income, yearly_income):
                        st.success("✅ Income updated successfully!")
                    else:
                        st.error("Failed to update income")
                else:
                    st.warning("Please enter a valid monthly income")
    
    with col2:
        st.subheader("📊 Income Overview")
        
        if current_income:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">₹{current_income['monthly_income']:.2f}</div>
                <div class="metric-label">Monthly Income</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card" style="margin-top: 10px;">
                <div class="metric-value">₹{current_income['yearly_income']:.2f}</div>
                <div class="metric-label">Yearly Income</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Calculate savings
            summary = db.get_expense_summary(username)
            monthly_savings = current_income['monthly_income'] - summary['monthly_average']
            savings_rate = (monthly_savings / current_income['monthly_income'] * 100) if current_income['monthly_income'] > 0 else 0
            
            st.markdown(f"""
            <div class="metric-card" style="margin-top: 10px;">
                <div class="metric-value" style="color: {'#28a745' if monthly_savings >= 0 else '#dc3545'};">
                    ₹{monthly_savings:.2f}
                </div>
                <div class="metric-label">Monthly Savings ({savings_rate:.1f}%)</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No income information set. Please add your income to get personalized insights.")

def show_analysis():
    """Display AI-powered expense analysis."""
    st.header("📈 AI-Powered Analysis")
    
    db = get_database()
    ai = get_ai_analyzer()
    username = st.session_state.username
    
    # Get data
    expenses = db.get_user_expenses(username, limit=500)
    income = db.get_income(username)
    
    if not expenses:
        st.warning("⚠️ No expense data available for analysis. Please add some expenses first.")
        return
    
    # Analysis options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        analysis_type = st.selectbox(
            "Select Analysis Type",
            ["Complete Analysis", "Category Breakdown", "Spending Trends", "Monthly Comparison"]
        )
    
    with col2:
        if st.button("🔄 Refresh Analysis", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Generate analysis
    with st.spinner("🤖 AI is analyzing your expenses..."):
        if analysis_type == "Complete Analysis":
            analysis = ai.analyze_expenses(expenses, income)
            st.markdown("### 📊 Complete Financial Analysis")
            st.markdown(analysis)
        
        elif analysis_type == "Category Breakdown":
            st.markdown("### 📁 Category Breakdown")
            summary = db.get_expense_summary(username)
            
            if summary['category_breakdown']:
                # Create detailed category chart with lazy loading
                with st.spinner("Loading category chart..."):
                    categories = summary['category_breakdown']
                    df = pd.DataFrame(list(categories.items()), columns=['Category', 'Amount'])
                    df = df.sort_values('Amount', ascending=False)
                    
                    fig = px.bar(
                        df,
                        x='Category',
                        y='Amount',
                        color='Amount',
                        color_continuous_scale='Viridis'
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
                # Category details
                for cat, amount in categories.items():
                    percentage = (amount / summary['total_expenses']) * 100
                    st.write(f"**{cat}**: ₹{amount:.2f} ({percentage:.1f}%)")
            else:
                st.info("No category data available")
        
        elif analysis_type == "Spending Trends":
            st.markdown("### 📈 Spending Trends")
            
            # Monthly trend with lazy loading
            with st.spinner("Loading spending trends..."):
                df = pd.DataFrame(expenses)
                df['date'] = pd.to_datetime(df['date'])
                df['month'] = df['date'].dt.to_period('M').astype(str)
                
                monthly_totals = df.groupby('month')['amount'].sum().reset_index()
                monthly_totals.columns = ['Month', 'Total']
                
                fig = px.line(
                    monthly_totals,
                    x='Month',
                    y='Total',
                    markers=True,
                    title='Monthly Spending Trend'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Insights
            insights = ai.get_spending_insights(expenses)
            st.markdown(f"""
            **📊 Quick Insights:**
            - **Total Spent**: ₹{insights['total']:.2f}
            - **Average Transaction**: ₹{insights['average']:.2f}
            - **Highest Expense**: ₹{insights['highest']:.2f}
            - **Lowest Expense**: ₹{insights['lowest']:.2f}
            - **Trend**: {insights['trend']}
            """)
        
        elif analysis_type == "Monthly Comparison":
            st.markdown("### 📅 Monthly Comparison")
            
            # Monthly comparison with lazy loading
            with st.spinner("Loading monthly comparison..."):
                df = pd.DataFrame(expenses)
                df['date'] = pd.to_datetime(df['date'])
                df['month'] = df['date'].dt.to_period('M').astype(str)
                
                monthly_data = df.groupby(['month', 'category'])['amount'].sum().reset_index()
                
                fig = px.bar(
                    monthly_data,
                    x='month',
                    y='amount',
                    color='category',
                    title='Monthly Expenses by Category',
                    barmode='stack'
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def show_budget_advice():
    """Display personalized budgeting advice."""
    st.header("💡 Personalized Budget Advice")
    
    db = get_database()
    ai = get_ai_analyzer()
    username = st.session_state.username
    
    # Get data
    expenses = db.get_user_expenses(username, limit=500)
    income = db.get_income(username)
    
    if not expenses:
        st.warning("⚠️ No expense data available. Please add some expenses first.")
        return
    
    # Financial goals input
    st.subheader("🎯 Your Financial Goals")
    financial_goals = st.text_area(
        "What are your financial goals?",
        placeholder="e.g., Save for a house, pay off debt, build emergency fund...",
        height=100
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💡 Get Personalized Advice", use_container_width=True):
            with st.spinner("🤖 Generating personalized budgeting advice..."):
                advice = ai.get_budgeting_advice(expenses, income, financial_goals)
                
                st.markdown("---")
                st.markdown("### 📋 Your Personalized Budget Plan")
                st.markdown(advice)
    
    with col2:
        if st.button("💰 Get Money-Saving Tips", use_container_width=True):
            with st.spinner("🤖 Analyzing your expenses for money-saving opportunities..."):
                tips = ai.get_money_saving_tips(expenses, income)
                
                st.markdown("---")
                st.markdown("### 💡 Personalized Money-Saving Tips")
                st.markdown(tips)
    
    # Quick budget tips
    st.markdown("---")
    st.subheader("⚡ Quick Budget Tips")
    
    summary = db.get_expense_summary(username)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **💰 50/30/20 Rule:**
        - **50%** for Needs (rent, utilities, groceries)
        - **30%** for Wants (entertainment, dining out)
        - **20%** for Savings & Debt Repayment
        """)
    
    with col2:
        if income:
            monthly_income = income['monthly_income']
            needs = monthly_income * 0.5
            wants = monthly_income * 0.3
            savings = monthly_income * 0.2
            
            st.markdown(f"""
            **📊 Your Budget Allocation:**
            - **Needs**: ₹{needs:.2f}
            - **Wants**: ₹{wants:.2f}
            - **Savings**: ₹{savings:.2f}
            """)
        else:
            st.info("Set your income to see personalized budget allocation")

def show_ai_chat():
    """Display AI chat interface."""
    st.header("🤖 AI Financial Assistant")
    
    db = get_database()
    ai = get_ai_analyzer()
    username = st.session_state.username
    
    # Get context
    summary = db.get_expense_summary(username)
    
    # Chat container
    st.markdown("### 💬 Chat with your Financial AI")
    st.caption("Ask questions about your expenses, budgeting tips, or financial advice!")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="user-message">
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="assistant-message">
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Type your message...",
            placeholder="e.g., How can I reduce my spending?",
            key="chat_input"
        )
        submit = st.form_submit_button("Send", use_container_width=True)
        
        if submit and user_input:
            # Add user message
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })
            
            # Get AI response
            with st.spinner("🤖 Thinking..."):
                response = ai.chat_response(
                    user_input,
                    st.session_state.chat_history,
                    summary
                )
            
            # Add AI response
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response
            })
            
            # Save to database
            db.add_chat_message(username, 'user', user_input)
            db.add_chat_message(username, 'assistant', response)
            
            st.rerun()
    
    # Quick actions
    st.markdown("---")
    st.subheader("⚡ Quick Questions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Analyze my spending", use_container_width=True):
            st.session_state.chat_history.append({
                'role': 'user',
                'content': "Can you analyze my spending patterns?"
            })
            with st.spinner("🤖 Analyzing..."):
                response = ai.chat_response(
                    "Can you analyze my spending patterns?",
                    st.session_state.chat_history,
                    summary
                )
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response
            })
            st.rerun()
    
    with col2:
        if st.button("💡 Budget tips", use_container_width=True):
            st.session_state.chat_history.append({
                'role': 'user',
                'content': "Give me some budgeting tips based on my expenses."
            })
            with st.spinner("🤖 Generating tips..."):
                response = ai.chat_response(
                    "Give me some budgeting tips based on my expenses.",
                    st.session_state.chat_history,
                    summary
                )
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response
            })
            st.rerun()
    
    with col3:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

# Main app entry point
def main():
    """Main application entry point."""
    init_session_state()
    
    # Create logs directory if it doesn't exist
    import os
    os.makedirs("logs", exist_ok=True)
    
    # Show appropriate page based on login status
    if st.session_state.logged_in:
        show_main_app()
    else:
        show_login_page()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>💰 Expense Manager v1.0 | Created by Aryan Chavan</p>
        <p>Powered by Streamlit & Groq AI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
