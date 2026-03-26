"""
AI Analysis module using Groq API for expense analysis and budgeting advice.
Optimized for performance with caching and efficient API calls.
"""

import streamlit as st
import os
from groq import Groq
from typing import List, Dict, Any, Optional
from loguru import logger
import json
from datetime import datetime

# Configure logging
logger.add("logs/ai_analysis.log", rotation="10 MB", retention="30 days", level="INFO")

class AIAnalyzer:
    """Handles all AI-powered analysis and chat functionality."""
    
    def __init__(self):
        """Initialize Groq client."""
        self.client = None
        self.model = "llama-3.3-70b-versatile"  # Current supported model (fast and efficient)
        self.is_configured = False
        
        try:
            # Try to get API key from Streamlit secrets
            api_key = None
            try:
                api_key = st.secrets["groq"]["api_key"]
                logger.info("API key loaded from Streamlit secrets")
            except (KeyError, FileNotFoundError):
                # Fallback to environment variable
                api_key = os.environ.get("GROQ_API_KEY")
                if api_key:
                    logger.info("API key loaded from environment variable")
            
            if api_key and api_key != "your_groq_api_key_here":
                self.client = Groq(api_key=api_key)
                self.is_configured = True
                logger.info("AI Analyzer initialized with Groq API")
            else:
                logger.warning("Groq API key not configured. AI features will be disabled.")
                self.is_configured = False
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            self.is_configured = False
    
    def _get_completion(self, messages: List[Dict], max_tokens: int = 1024) -> str:
        """Get completion from Groq API with error handling."""
        if not self.is_configured or not self.client:
            return "Error: AI features are disabled. Please configure your Groq API key in Streamlit secrets or as an environment variable (GROQ_API_KEY)."
        
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error getting AI completion: {error_msg}")
            
            # Provide specific guidance based on error type
            if "organization_restricted" in error_msg.lower():
                return """Error: Your Groq organization has been restricted. This is an account-level issue.

To resolve this:
1. Check your Groq account status at https://console.groq.com
2. Contact Groq support if you believe this was done in error
3. Use a different Groq API key from another account

The app will continue to work without AI features."""
            elif "invalid_api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                return """Error: Invalid Groq API key. Please check your API key configuration.

To resolve this:
1. Verify your API key at https://console.groq.com
2. Update the key in Streamlit Cloud secrets or environment variables
3. Ensure the key has not expired"""
            elif "model_decommissioned" in error_msg.lower() or "decommissioned" in error_msg.lower():
                return """Error: The AI model has been decommissioned by Groq.

This is a model availability issue. The app developer needs to:
1. Update the model in ai_analyzer.py to a currently supported model
2. Check available models at https://console.groq.com/docs/models
3. Common current models: llama3-8b-8192, mixtral-8x7b-32768, gemma-7b-it

The app will continue to work without AI features."""
            else:
                return f"Error: Unable to get AI response. Details: {error_msg}"
    
    def analyze_expenses(self, expenses: List[Dict], income: Optional[Dict] = None) -> str:
        """Analyze expenses and provide insights."""
        try:
            # Prepare expense data
            total_expenses = sum(e['amount'] for e in expenses)
            categories = {}
            for expense in expenses:
                cat = expense.get('category', 'Other')
                categories[cat] = categories.get(cat, 0) + expense['amount']
            
            # Create analysis prompt
            expense_summary = f"""
            Total Expenses: ${total_expenses:.2f}
            Number of Transactions: {len(expenses)}
            Category Breakdown:
            {json.dumps(categories, indent=2)}
            """
            
            income_info = ""
            if income:
                monthly_income = income.get('monthly_income', 0)
                yearly_income = income.get('yearly_income', 0)
                savings = monthly_income - total_expenses
                savings_rate = (savings / monthly_income * 100) if monthly_income > 0 else 0
                
                income_info = f"""
                Monthly Income: ${monthly_income:.2f}
                Yearly Income: ${yearly_income:.2f}
                Current Savings: ${savings:.2f}
                Savings Rate: {savings_rate:.1f}%
                """
            
            prompt = f"""Analyze the following expense data and provide detailed insights:

            EXPENSE DATA:
            {expense_summary}
            
            {f'INCOME INFORMATION:{income_info}' if income_info else ''}
            
            Please provide:
            1. A summary of spending patterns
            2. Top spending categories and their significance
            3. Areas where spending could be optimized
            4. Specific actionable advice for better budgeting
            5. If income data is available, analyze savings rate and financial health
            6. Recommendations for the next month
            
            Format the response in a clear, easy-to-read manner with bullet points and sections.
            """
            
            messages = [
                {"role": "system", "content": "You are a professional financial advisor and expense analyst. Provide clear, actionable advice based on the expense data provided."},
                {"role": "user", "content": prompt}
            ]
            
            analysis = self._get_completion(messages, max_tokens=1500)
            logger.info("Expense analysis completed successfully")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing expenses: {e}")
            return f"Error analyzing expenses: {str(e)}"
    
    def get_budgeting_advice(self, expenses: List[Dict], income: Optional[Dict] = None, 
                            financial_goals: str = "") -> str:
        """Get personalized budgeting advice."""
        try:
            total_expenses = sum(e['amount'] for e in expenses)
            categories = {}
            for expense in expenses:
                cat = expense.get('category', 'Other')
                categories[cat] = categories.get(cat, 0) + expense['amount']
            
            # Sort categories by amount
            sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
            
            prompt = f"""Based on the following financial data, provide personalized budgeting advice:

            CURRENT SPENDING:
            Total Monthly Expenses: ${total_expenses:.2f}
            Top Spending Categories:
            {chr(10).join(f'- {cat}: ${amount:.2f}' for cat, amount in sorted_categories[:5])}
            
            {f'Monthly Income: ${income.get("monthly_income", 0):.2f}' if income else 'Income: Not specified'}
            {f'Financial Goals: {financial_goals}' if financial_goals else ''}
            
            Please provide:
            1. The 50/30/20 rule breakdown (Needs/Wants/Savings)
            2. Specific budget allocations for each category
            3. Tips to reduce spending in top categories
            4. Emergency fund recommendations
            5. Short-term and long-term financial goals
            6. Monthly budget template
            
            Make the advice practical and actionable.
            """
            
            messages = [
                {"role": "system", "content": "You are an expert budgeting coach. Provide practical, personalized budgeting advice that is easy to implement."},
                {"role": "user", "content": prompt}
            ]
            
            advice = self._get_completion(messages, max_tokens=1500)
            logger.info("Budgeting advice generated successfully")
            return advice
            
        except Exception as e:
            logger.error(f"Error generating budgeting advice: {e}")
            return f"Error generating budgeting advice: {str(e)}"
    
    def chat_response(self, message: str, chat_history: List[Dict], 
                     expense_context: Optional[Dict] = None) -> str:
        """Generate chat response with context."""
        try:
            # Build context from expense data
            context = ""
            if expense_context:
                context = f"""
                USER'S FINANCIAL CONTEXT:
                - Total Expenses: ${expense_context.get('total_expenses', 0):.2f}
                - Monthly Average: ${expense_context.get('monthly_average', 0):.2f}
                - Top Categories: {json.dumps(expense_context.get('category_breakdown', {}), indent=2)}
                """
            
            # Build messages with history
            messages = [
                {"role": "system", "content": f"""You are a helpful financial assistant for an expense manager app. 
                You help users understand their spending, provide budgeting advice, and answer financial questions.
                {context}
                
                Be friendly, helpful, and provide actionable advice. Keep responses concise but informative.
                """}
            ]
            
            # Add chat history (last 10 messages for context)
            for msg in chat_history[-10:]:
                messages.append({"role": msg['role'], "content": msg['content']})
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            response = self._get_completion(messages, max_tokens=800)
            logger.info("Chat response generated successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            return f"Error: Unable to generate response. {str(e)}"
    
    def get_spending_insights(self, expenses: List[Dict]) -> Dict[str, Any]:
        """Get detailed spending insights and metrics."""
        try:
            if not expenses:
                return {
                    "total": 0,
                    "average": 0,
                    "highest": 0,
                    "lowest": 0,
                    "categories": {},
                    "trend": "No data"
                }
            
            amounts = [e['amount'] for e in expenses]
            categories = {}
            
            for expense in expenses:
                cat = expense.get('category', 'Other')
                categories[cat] = categories.get(cat, 0) + expense['amount']
            
            # Calculate trend (comparing last 2 months)
            current_month = datetime.now().strftime("%Y-%m")
            # Handle year boundary correctly
            if datetime.now().month == 1:
                last_month = datetime.now().replace(year=datetime.now().year-1, month=12).strftime("%Y-%m")
            else:
                last_month = datetime.now().replace(month=datetime.now().month-1).strftime("%Y-%m")
            
            current_month_expenses = [e for e in expenses if e.get('month') == current_month]
            last_month_expenses = [e for e in expenses if e.get('month') == last_month]
            
            current_total = sum(e['amount'] for e in current_month_expenses)
            last_total = sum(e['amount'] for e in last_month_expenses)
            
            if last_total > 0:
                trend_percent = ((current_total - last_total) / last_total) * 100
                trend = f"{'↑' if trend_percent > 0 else '↓'} {abs(trend_percent):.1f}%"
            else:
                trend = "No comparison data"
            
            insights = {
                "total": sum(amounts),
                "average": sum(amounts) / len(amounts),
                "highest": max(amounts),
                "lowest": min(amounts),
                "categories": categories,
                "trend": trend,
                "transaction_count": len(expenses)
            }
            
            logger.info("Spending insights generated successfully")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating spending insights: {e}")
            return {
                "total": 0,
                "average": 0,
                "highest": 0,
                "lowest": 0,
                "categories": {},
                "trend": "Error calculating"
            }

# Singleton instance
@st.cache_resource
def get_ai_analyzer():
    """Get cached AI analyzer instance for performance."""
    return AIAnalyzer()
