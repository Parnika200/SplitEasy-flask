# SplitEasy

A full-stack **expense management web application** built with Flask and SQLAlchemy that helps users track personal expenses, manage group expenses, and get **AI-powered spending insights** using Google Gemini.

The project combines traditional expense-management functionality with Generative AI to provide natural-language assistance and personalized spending analysis.

---

## ✨ Features

### 👤 Personal Expense Management

* Add, edit, and delete expenses
* Track expense amount, description, date, and category
* View personal spending history
* Organize expenses by category

### 👥 Group Expense Management

* Create and manage expense groups
* Add members to groups
* Track group-related expenses
* View expenses associated with specific groups
* Store individual expense splits between group members

### 🤖 AI Expense Assistant

Ask questions about your expenses using natural language.

Examples:

```text
How much did I spend this month?
How many groups am I in?
How many expenses are in my Trip group?
Which group has the most expenses?
How much did I spend on Food?
```

The AI uses the user's expense and group data to generate answers while being instructed not to invent unavailable information.

### 📊 AI Spending Insights

Generate an AI-powered analysis of spending habits.

The system analyzes:

* Total spending
* Number of expenses
* Average expense
* Spending by category
* Highest spending category
* Spending patterns
* Potential areas for reducing expenses

The AI response is returned as structured JSON and displayed through separate UI cards.

### 🔐 Authentication

* User registration and login
* Session-based authentication
* User-specific expense data
* Protected application routes

---

## 🧠 AI Architecture

The application uses **Google Gemini through LangChain**.

```text
User
 │
 ▼
Flask Application
 │
 ├── Personal Expenses
 │
 ├── Group Data
 │
 └── Spending Statistics
 │
 ▼
Prompt Construction
 │
 ▼
Google Gemini
 │
 ▼
AI Response
 │
 ▼
Flask
 │
 ▼
User Interface
```

The application performs important calculations such as totals and category-wise spending using Python/database data first. Gemini is then used to interpret the structured information and generate human-readable insights.

---

## 🛠️ Tech Stack

### Backend

* Python
* Flask
* SQLAlchemy

### Database

* SQL database
* Flask-SQLAlchemy

### AI

* Google Gemini
* LangChain
* `langchain-google-genai`

### Frontend

* HTML
* CSS
* Jinja2

### Authentication

* Flask sessions

---

## 📂 Project Structure

```text
expense-manager/
│
├── app.py
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── expenses.html
│   ├── groups.html
│   ├── ai_assistant.html
│   └── spending_insights.html
│
├── static/
│   └── css/
│       └── style.css
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repository.git
```

```bash
cd your-repository
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

If you haven't created `requirements.txt` yet:

```powershell
pip install flask flask-sqlalchemy python-dotenv langchain-google-genai
```

### 4. Create `.env`

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key
```

Get a Gemini API key from:

https://aistudio.google.com/app/apikey

**Never commit your `.env` file to GitHub.**

Add this to `.gitignore`:

```text
.env
venv/
__pycache__/
*.pyc
```

---

## 🤖 Gemini Configuration

The application initializes Gemini through LangChain:

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)
```

The same LLM instance is used by the AI-related routes.

---

## 📊 AI Spending Insights

The spending insights feature first calculates useful statistics:

```text
Total Spending
Number of Expenses
Average Expense
Category-wise Spending
```

These values are sent to Gemini.

The model returns structured information such as:

```json
{
    "highest_category": "Shopping",
    "highest_amount": 3000,
    "pattern": "60% of spending is on Shopping.",
    "suggestion": "Consider reducing unnecessary shopping expenses.",
    "summary": "You spent ₹5000 across 3 expenses."
}
```

The Flask application then displays these values as separate UI cards.

This approach separates:

```text
Data Processing → Python
AI Interpretation → Gemini
Presentation → HTML/CSS
```

---

## 👥 Group Data Model

The application uses separate models for groups, members, and expense splits.

```text
User
 │
 ├── Group
 │     │
 │     ├── GroupMember
 │     │
 │     └── Expense
 │
 └── ExpenseSplit
```

### Group

Stores information about an expense group.

### GroupMember

Connects users with groups.

### ExpenseSplit

Stores how an expense is divided between individual users.

This structure allows the AI assistant to answer group-related questions using database information.

---

## 🔒 Data Safety

The AI assistant only receives data belonging to the currently logged-in user.

User identification is handled using Flask sessions:

```python
session["user_id"]
```

The application retrieves expenses and groups using this user ID before constructing the AI prompt.

The AI is also instructed:

```text
Do not invent expenses or amounts.
Use only the provided data.
```

## 👩‍💻 Author

**Parnika**

Built as a practical full-stack project combining **web development, databases, and Generative AI**.
