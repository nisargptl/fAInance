# fAInance - Personal Finance Management System

fAInance is a smart personal finance management system designed to help you manage your transactions, analyze spending, and provide easy ways to store, edit, delete, and review financial records. It also supports CSV import/export and integrates with an AI assistant to handle tasks interactively.

---

## Features

- **Store Transactions**: Add income or expenses directly to the system.
- **Search, Edit, and Delete Transactions**: Easily search for transactions by category or date, and modify or remove them.
- **Graphical Analysis**: Visualize your spending by category using interactive charts.
- **CSV Export/Import**: Export transactions to a CSV file and import transactions from a CSV file.
- **Bulk Operations via SQL**: Execute custom SQL queries for bulk transaction modifications.
- **LLM Integration**: Use AI-powered ConversableAgents to store, search, edit, and delete transactions.

---

## Setup and Installation

Follow these steps to set up and run **fAInance**:

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/fAInance.git
cd fAInance
```

### 2. Set Up a Virtual Environment (Optional but Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Add Your OpenAI API Key

Create a `.env` file in the root directory and add your OpenAI API key like this:

```plaintext
OPENAI_API_KEY=your_openai_api_key_here
```

Replace `your_openai_api_key_here` with your actual API key.

---

## Usage

### Running the Application

To start the application, run:

```bash
python main.py
```

Once started, you will see a command-line interface with options to:

1. **Create/Reset Database**: Initialize a new database with sample data.
2. **Store Transaction**: Add a new transaction.
3. **Search, Edit, Delete, or Analyze Transaction**: Perform unified search, edit, delete, and analysis tasks.
4. **Export Transactions to CSV**: Save transactions to a CSV file.
5. **Import Transactions from CSV**: Load transactions from a CSV file.
6. **Show Spending by Category (Graph)**: Visualize spending data as a bar chart.
7. **Execute Custom SQL Query**: Run custom SQL queries for bulk operations.

---

## Example SQL Queries for Bulk Operations

### Delete Multiple Transactions

```sql
DELETE FROM transactions WHERE category = 'Entertainment';
```

### Update Multiple Transactions

```sql
UPDATE transactions SET amount = amount * 1.05 WHERE category = 'Fuel';
```

---

## Project Structure

```
fAInance/
├── transactions.db        # The SQLite database file
├── requirements.txt       # Project dependencies
├── README.md              # Project documentation
├── .gitignore             # Ignored files for version control
└── .env                   # Environment variables (e.g., API keys)
```

---

## Dependencies

- Python 3.7+
- **Matplotlib** for data visualization
- **SQLite** for transaction storage
- **ConversableAgent** for AI-powered interactions
- **OpenAI** API for LLM integration
- **Dotenv** for environment variable management

---

## Future Enhancements

- **Budget Tracking**: Set budget limits per category and alert users when exceeding them.
- **Dynamic Visualizations**: Add support for getting visualizations from conversations.
- **Mobile App**: Build a mobile interface for easier access to fAInance on the go.
- **Reports and Forecasts**: Add detailed reports and future expense/income forecasts based on historical data.

---

