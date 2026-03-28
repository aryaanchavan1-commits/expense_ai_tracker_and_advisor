"""
Database layer using JSON for storing user data and expenses.
Optimized for performance with caching and efficient queries.
"""

import json
import hashlib
import os
from datetime import datetime
from typing import Optional, Dict, List, Any
import streamlit as st
from loguru import logger
from pathlib import Path
import threading
from functools import lru_cache

# Configure logging
logger.add("logs/app.log", rotation="10 MB", retention="30 days", level="INFO")

class DatabaseManager:
    """Manages all database operations using JSON files."""
    
    def __init__(self, db_file: str = "dbms.json"):
        """Initialize JSON database manager."""
        self.db_file = db_file
        self.lock = threading.Lock()
        self._ensure_db_file()
        logger.info("JSON Database initialized successfully")
    
    def _ensure_db_file(self):
        """Ensure the database file exists with proper structure."""
        if not os.path.exists(self.db_file):
            initial_data = {
                "users": {},
                "expenses": {},
                "income": {},
                "chat_history": {}
            }
            self._save_data(initial_data)
            logger.info(f"Created new database file: {self.db_file}")
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file with thread safety."""
        with self.lock:
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.error(f"Error loading database: {e}")
                return {
                    "users": {},
                    "expenses": {},
                    "income": {},
                    "chat_history": {}
                }
    
    def _save_data(self, data: Dict[str, Any]) -> bool:
        """Save data to JSON file with thread safety."""
        with self.lock:
            try:
                with open(self.db_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return True
            except Exception as e:
                logger.error(f"Error saving database: {e}")
                return False
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, password: str, email: str = "") -> bool:
        """Create a new user account."""
        try:
            data = self._load_data()
            
            # Check if user exists
            if username in data["users"]:
                logger.warning(f"User {username} already exists")
                return False
            
            # Create user document
            user_data = {
                "username": username,
                "password_hash": self._hash_password(password),
                "email": email,
                "created_at": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat()
            }
            
            data["users"][username] = user_data
            
            if self._save_data(data):
                logger.info(f"User {username} created successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user credentials."""
        try:
            data = self._load_data()
            
            if username not in data["users"]:
                logger.warning(f"User {username} not found")
                return False
            
            user_data = data["users"][username]
            password_hash = self._hash_password(password)
            
            if user_data['password_hash'] == password_hash:
                # Update last login
                user_data['last_login'] = datetime.now().isoformat()
                data["users"][username] = user_data
                self._save_data(data)
                logger.info(f"User {username} authenticated successfully")
                return True
            
            logger.warning(f"Invalid password for user {username}")
            return False
        except Exception as e:
            logger.error(f"Error authenticating user {username}: {e}")
            return False
    
    def add_expense(self, username: str, expense_name: str, amount: float, 
                   category: str = "Other", description: str = "") -> bool:
        """Add a new expense for a user."""
        try:
            data = self._load_data()
            
            expense_id = f"{username}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            expense_data = {
                "username": username,
                "expense_name": expense_name,
                "amount": amount,
                "category": category,
                "description": description,
                "date": datetime.now().isoformat(),
                "month": datetime.now().strftime("%Y-%m"),
                "year": datetime.now().year,
                "expense_id": expense_id
            }
            
            if username not in data["expenses"]:
                data["expenses"][username] = {}
            
            data["expenses"][username][expense_id] = expense_data
            
            if self._save_data(data):
                logger.info(f"Expense added for {username}: {expense_name} - ₹{amount}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding expense for {username}: {e}")
            return False
    
    @st.cache_data(ttl=60, show_spinner=False)
    def get_user_expenses(_self, username: str, limit: int = 100) -> List[Dict]:
        """Get all expenses for a user with caching."""
        try:
            data = _self._load_data()
            
            if username not in data["expenses"]:
                logger.info(f"No expenses found for {username}")
                return []
            
            expenses = list(data["expenses"][username].values())
            
            # Sort by date descending
            expenses.sort(key=lambda x: x['date'], reverse=True)
            
            # Apply limit
            expenses = expenses[:limit]
            
            logger.info(f"Retrieved {len(expenses)} expenses for {username}")
            return expenses
        except Exception as e:
            logger.error(f"Error getting expenses for {username}: {e}")
            return []
    
    def get_expenses_by_month(self, username: str, month: str) -> List[Dict]:
        """Get expenses for a specific month."""
        try:
            data = self._load_data()
            
            if username not in data["expenses"]:
                logger.info(f"No expenses found for {username}")
                return []
            
            expenses = [
                exp for exp in data["expenses"][username].values()
                if exp.get('month') == month
            ]
            
            expenses.sort(key=lambda x: x['date'], reverse=True)
            logger.info(f"Retrieved {len(expenses)} expenses for {username} in {month}")
            return expenses
        except Exception as e:
            logger.error(f"Error getting expenses for {username} in {month}: {e}")
            return []
    
    def set_income(self, username: str, monthly_income: float, 
                  yearly_income: float = 0) -> bool:
        """Set user's income information."""
        try:
            data = self._load_data()
            
            income_data = {
                "username": username,
                "monthly_income": monthly_income,
                "yearly_income": yearly_income if yearly_income > 0 else monthly_income * 12,
                "updated_at": datetime.now().isoformat()
            }
            
            data["income"][username] = income_data
            
            if self._save_data(data):
                logger.info(f"Income updated for {username}: ₹{monthly_income}/month")
                return True
            return False
        except Exception as e:
            logger.error(f"Error setting income for {username}: {e}")
            return False
    
    @st.cache_data(ttl=60, show_spinner=False)
    def get_income(_self, username: str) -> Optional[Dict]:
        """Get user's income information with caching."""
        try:
            data = _self._load_data()
            
            if username in data["income"]:
                income_data = data["income"][username]
                logger.info(f"Retrieved income for {username}")
                return income_data
            
            logger.info(f"No income record found for {username}")
            return None
        except Exception as e:
            logger.error(f"Error getting income for {username}: {e}")
            return None
    
    def add_chat_message(self, username: str, role: str, content: str) -> bool:
        """Add a chat message to history."""
        try:
            data = self._load_data()
            
            message_id = f"{username}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            message_data = {
                "username": username,
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "message_id": message_id
            }
            
            if username not in data["chat_history"]:
                data["chat_history"][username] = {}
            
            data["chat_history"][username][message_id] = message_data
            
            if self._save_data(data):
                logger.info(f"Chat message added for {username}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding chat message for {username}: {e}")
            return False
    
    def get_chat_history(self, username: str, limit: int = 50) -> List[Dict]:
        """Get chat history for a user."""
        try:
            data = self._load_data()
            
            if username not in data["chat_history"]:
                logger.info(f"No chat history found for {username}")
                return []
            
            messages = list(data["chat_history"][username].values())
            
            # Sort by timestamp
            messages.sort(key=lambda x: x['timestamp'])
            
            # Apply limit
            messages = messages[-limit:] if len(messages) > limit else messages
            
            logger.info(f"Retrieved {len(messages)} chat messages for {username}")
            return messages
        except Exception as e:
            logger.error(f"Error getting chat history for {username}: {e}")
            return []
    
    @st.cache_data(ttl=60, show_spinner=False)
    def get_expense_summary(_self, username: str) -> Dict[str, Any]:
        """Get expense summary statistics for a user with caching."""
        try:
            expenses = _self.get_user_expenses(username, limit=1000)
            
            if not expenses:
                return {
                    "total_expenses": 0,
                    "monthly_average": 0,
                    "category_breakdown": {},
                    "expense_count": 0
                }
            
            total = sum(e['amount'] for e in expenses)
            categories = {}
            
            for expense in expenses:
                cat = expense.get('category', 'Other')
                categories[cat] = categories.get(cat, 0) + expense['amount']
            
            # Calculate monthly average
            months = set(e.get('month', '') for e in expenses)
            monthly_avg = total / len(months) if months else 0
            
            summary = {
                "total_expenses": total,
                "monthly_average": monthly_avg,
                "category_breakdown": categories,
                "expense_count": len(expenses)
            }
            
            logger.info(f"Generated expense summary for {username}")
            return summary
        except Exception as e:
            logger.error(f"Error generating summary for {username}: {e}")
            return {
                "total_expenses": 0,
                "monthly_average": 0,
                "category_breakdown": {},
                "expense_count": 0
            }
    
    def delete_expense(self, username: str, expense_id: str) -> bool:
        """Delete an expense."""
        try:
            data = self._load_data()
            
            if username in data["expenses"] and expense_id in data["expenses"][username]:
                del data["expenses"][username][expense_id]
                
                if self._save_data(data):
                    logger.info(f"Expense {expense_id} deleted for {username}")
                    return True
            else:
                logger.warning(f"Expense {expense_id} not found for {username}")
            return False
        except Exception as e:
            logger.error(f"Error deleting expense {expense_id}: {e}")
            return False
    
    def get_all_users(self) -> List[str]:
        """Get list of all usernames."""
        try:
            data = self._load_data()
            return list(data["users"].keys())
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    def backup_database(self, backup_path: str = "dbms_backup.json") -> bool:
        """Create a backup of the database."""
        try:
            data = self._load_data()
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            return False

# Singleton instance
@st.cache_resource
def get_database():
    """Get cached database instance for performance."""
    return DatabaseManager()
