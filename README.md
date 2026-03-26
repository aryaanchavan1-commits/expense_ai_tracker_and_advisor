# 💰 Expense Manager App

**Created by Aryan Chavan**

A powerful, AI-powered expense management application built with Streamlit, featuring Groq API integration for intelligent financial analysis and budgeting advice.

## ✨ Features

- 🔐 **User Authentication** - Secure login/registration system
- 📊 **Financial Dashboard** - Real-time expense overview with interactive charts
- ➕ **Expense Tracking** - Easy expense entry with categories
- 💵 **Income Management** - Track monthly and yearly income
- 📈 **AI-Powered Analysis** - Intelligent expense analysis using Groq API
- 💡 **Budget Advice** - Personalized budgeting recommendations
- 🤖 **AI Chat** - Interactive financial assistant
- 📱 **Modern UI** - Clean, responsive design with top navigation
- ⚡ **Optimized Performance** - Fast loading with caching

## 🚀 Quick Start

### Prerequisites

- Python 3.13 or higher
- Groq API key (get it from [Groq Console](https://console.groq.com))

### Installation

1. **Clone or download this repository**
'''bash
https://github.com/aryaanchavan1-commits/expense_ai_tracker_and_advisor.git
'''
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```



4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   
   Navigate to `http://localhost:8501`



### 1. **Register/Login**
   - Create a new account or login with existing credentials
   - Your data is securely stored in JSON database

### 2. **Dashboard**
   - View your financial overview
   - See expense breakdown by category
   - Track spending trends over time

### 3. **Add Expenses**
   - Enter expense name and amount
   - Select category from dropdown
   - Add optional description

### 4. **Income Management**
   - Set your monthly income
   - Optionally set yearly income
   - View savings calculations

### 5. **AI Analysis**
   - Get comprehensive expense analysis
   - View category breakdowns
   - Analyze spending trends
   - Compare monthly expenses

### 6. **Budget Advice**
   - Receive personalized budgeting tips
   - Get 50/30/20 rule breakdown
   - Set financial goals and get advice

### 7. **AI Chat**
   - Ask questions about your finances
   - Get instant budgeting advice
   - Quick action buttons for common queries



### Customization

Edit `config.py` to customize:
- Expense categories
- AI model settings
- Performance parameters
- UI theme colors


## ⚡ Performance Optimizations

This app is optimized for fast performance:

- **Caching**: Database and AI analyzer instances are cached
- **Efficient Queries**: JSON database queries are optimized
- **Lazy Loading**: Components load only when needed
- **Session State**: Minimal session state usage
- **Async Operations**: Non-blocking UI updates

## 🔒 Security Features

- Password hashing using SHA-256
- Secure session management
- API keys stored in Streamlit secrets
- No sensitive data in code

## 📊 Database Schema

### Users Collection
- username (ID)
- password_hash
- email
- created_at
- last_login

### Expenses Collection
- expense_id (ID)
- username
- expense_name
- amount
- category
- description
- date
- month
- year

### Income Collection
- username_income (ID)
- username
- monthly_income
- yearly_income
- updated_at

### Chat History Collection
- message_id (ID)
- username
- role (user/assistant)
- content
- timestamp

## 🛠️ Troubleshooting

### Common Issues

1. **"Module not found" error**
   ```bash
   pip install -r requirements.txt
   ```

2. **"Groq API key not found"**
   - Check your `.streamlit/secrets.toml` file
   - Ensure the API key is correct

3. **Database errors**
   - Delete the `dbms.json` file and restart
   - Check file permissions

4. **Slow performance on Streamlit Cloud**
   - The app uses caching to optimize performance
   - First load may be slower due to cold start
   - Subsequent loads should be fast

## 📝 Logging

Logs are stored in the `logs/` directory:
- `app.log` - General application logs
- `ai_analysis.log` - AI analysis logs

Logs are automatically rotated (10 MB) and retained for 30 days.

## 🤝 Contributing

This app was created by Aryan Chavan. Feel free to fork and modify for your needs.

## 📄 License

This project is open source and available for personal and commercial use.

## 🙏 Acknowledgments

- **Streamlit** - For the amazing web framework
- **Groq** - For the powerful AI API
- **Plotly** - For beautiful interactive charts

---

**Created with ❤️ by Aryan Chavan**
