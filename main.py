import sqlite3
import random
import csv
from datetime import date, timedelta
from typing import Annotated, Literal, Optional, Any, List, Tuple
import matplotlib.pyplot as plt
from autogen import ConversableAgent
import openai
from dotenv import load_dotenv
import os

load_dotenv()

# Database setup function
def create_sample_database(database_name):
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        expense BOOLEAN NOT NULL
    )
    ''')

    categories = ["Clothes", "Eating Out", "Entertainment", "Fuel", "General", "Gifts", "Holidays", "Kids", "Shopping", "Sports", "Travel", "Salary"]

    def random_date():
        today = date.today()
        days_ago = random.randint(0, 365)
        return (today - timedelta(days_ago)).isoformat()

    for _ in range(100):
        rn_data = random_date()
        category = random.choice(categories)
        if category == "Salary":
            amount = round(random.uniform(2000, 5000), 2)
            expense = 0
            description = "Monthly salary"
        else:
            amount = round(random.uniform(5, 500), 2)
            expense = 1
            description = f"{category} expense"

        cursor.execute('''
        INSERT INTO transactions (date, category, amount, description, expense)
        VALUES (?, ?, ?, ?, ?)''', (rn_data, category, amount, description, expense))

    conn.commit()
    conn.close()
    print("Database and sample data created successfully.")

# Export transactions to CSV
def export_transactions_to_csv(filename="transactions.csv"):
    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    transactions = cursor.fetchall()
    conn.close()

    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Date", "Category", "Amount", "Description", "Expense"])
        writer.writerows(transactions)

    print(f"Transactions exported successfully to {filename}.")

# Import transactions from CSV
def import_transactions_from_csv(filename="transactions.csv"):
    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()

    with open(filename, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute('''
            INSERT INTO transactions (date, category, amount, description, expense)
            VALUES (?, ?, ?, ?, ?)''', 
            (row["Date"], row["Category"], float(row["Amount"]), row["Description"], int(row["Expense"])))

    conn.commit()
    conn.close()
    print(f"Transactions imported successfully from {filename}.")

# Graphical analysis function
def show_spending_by_category():
    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()

    cursor.execute('''
    SELECT category, SUM(amount) FROM transactions WHERE expense = 1 GROUP BY category
    ''')
    data = cursor.fetchall()
    conn.close()

    categories = [item[0] for item in data]
    amounts = [item[1] for item in data]

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.bar(categories, amounts)
    plt.xlabel('Category')
    plt.ylabel('Amount Spent')
    plt.title('Spending by Category')
    plt.show()

# LLM Configuration
llm_config = {"model": "gpt-4o-mini"}

# Store transaction agent setup
storage_assistant = ConversableAgent(
    name="Assistant",
    system_message=f"You are a helpful AI assistant. You help in adding expense/income information into the database. Today's date is {date.today()}. Try to automatically figure out the fields required to store based on the provided context, ask follow-up queries only if you can't make it yourself. Before termination ask user if they want to add any other transaction. Return 'TERMINATE' when the task is completed.",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

# New Transaction Search Agent
search_assistant = ConversableAgent(
    name="SearchAssistant",
    system_message=f"""You are a helpful assistant that assists in finding the right transactions for editing or deletion. 
    Based on the provided filters, you should retrieve and display relevant transactions to the user.
    Once the user selects a transaction, you should proceed with the operation (edit/delete). 
    You must show the transaction ID, date, category, amount, and description.""",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

user_proxy = ConversableAgent(
    name="User",
    llm_config=False,
    is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
    human_input_mode="ALWAYS",
    code_execution_config=False,
)

# List transactions based on filters
@user_proxy.register_for_execution()
@search_assistant.register_for_llm(name="search_transactions", description="Filter and list transactions for editing or deletion")
def search_transactions(filter_category: Optional[str], filter_date: Optional[str]) -> Optional[List[Tuple[Any, ...]]]:
    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()

    # Dynamic query with filters
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []

    if filter_category:
        query += " AND category = ?"
        params.append(filter_category)

    if filter_date:
        query += " AND date = ?"
        params.append(filter_date)

    cursor.execute(query, params)
    transactions = cursor.fetchall()
    conn.close()

    if transactions:
        return transactions
    else:
        return None

# Edit transaction function
@user_proxy.register_for_execution()
@search_assistant.register_for_llm(name="edit_transaction", description="Edit an existing transaction")
def edit_transaction(transaction_id: int, new_date: str, new_category: str, new_amount: float, new_description: str, new_expense: bool) -> str:
    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE transactions 
    SET date = ?, category = ?, amount = ?, description = ?, expense = ?
    WHERE id = ?
    ''', (new_date, new_category, new_amount, new_description, new_expense, transaction_id))

    conn.commit()
    conn.close()
    return f"Transaction {transaction_id} updated successfully."

# Delete transaction function
@user_proxy.register_for_execution()
@search_assistant.register_for_llm(name="delete_transaction", description="Delete an existing transaction")
def delete_transaction(transaction_id: int) -> str:
    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()

    cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
    conn.commit()
    conn.close()
    return f"Transaction {transaction_id} deleted successfully."

# Execute raw SQL function for custom queries
@user_proxy.register_for_execution()
@search_assistant.register_for_llm(name="execute_sql", description="Function for executing custom SQL queries")
def execute_sql(query: str) -> Optional[List[Tuple[Any, ...]]]:
    try:
        conn = sqlite3.connect("transactions.db")
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None

# Unified option for search, edit, delete, and analyze transactions
def search_edit_delete_analyze():
    while True:
        print("\n--- Search, Edit, Delete, or Analyze Transactions ---")
        print("Disclaimer: Edit and delete options are for single transactions. For bulk operations, use Option 7.")
        filter_category = input("Enter category to filter by (or press Enter to skip): ")
        filter_date = input("Enter date to filter by (YYYY-MM-DD) (or press Enter to skip): ")

        # Search for transactions based on the filter
        transactions = search_transactions(filter_category, filter_date)
        if transactions:
            print("\nTransactions found:")
            for transaction in transactions:
                print(f"{transaction[0]} | {transaction[1]} | {transaction[2]} | {transaction[3]} | {transaction[4]} | {transaction[5]}")

            # Provide options after search
            print("\n1. Edit Transaction")
            print("2. Delete Transaction")
            print("3. Analyze Transactions")
            print("4. Return to Main Menu")

            sub_choice = input("Enter your choice (1-4): ")

            if sub_choice == '1':  # Edit transaction
                transaction_id = int(input("Enter transaction ID to edit: "))
                new_date = input("Enter new date (YYYY-MM-DD): ")
                new_category = input("Enter new category: ")
                new_amount = float(input("Enter new amount: "))
                new_description = input("Enter new description: ")
                new_expense = bool(int(input("Is it an expense? (1 for Yes, 0 for No): ")))
                message = edit_transaction(transaction_id, new_date, new_category, new_amount, new_description, new_expense)
                print(message)

            elif sub_choice == '2':  # Delete transaction
                transaction_id = int(input("Enter transaction ID to delete: "))
                confirmation = input(f"Are you sure you want to delete transaction {transaction_id}? (y/n): ").lower()
                if confirmation == 'y':
                    message = delete_transaction(transaction_id)
                    print(message)

            elif sub_choice == '3':  # Analyze Transactions
                show_spending_by_category()

            elif sub_choice == '4':  # Return to main menu
                break
            else:
                print("Invalid choice. Please try again.")
        else:
            print("No transactions found matching the criteria.")

# Main function to run the system
def main():
    openai.api_key = os.getenv("OPENAI_API_KEY")

    while True:
        print("\nPersonal Finance Management System")
        print("1. Create/Reset Database")
        print("2. Store Transaction")
        print("3. Search, Edit, Delete, or Analyze Transaction")
        print("4. Export Transactions to CSV")
        print("5. Import Transactions from CSV")
        print("6. Show Spending by Category (Graph)")
        print("7. Execute Custom SQL Query")
        print("8. Exit")

        choice = input("Enter your choice (1-8): ")

        if choice == '1':
            create_sample_database("transactions.db")
        elif choice == '2':
            storage_assistant.initiate_chat(user_proxy, message="Please enter your transaction details.")
        elif choice == '3':
            search_edit_delete_analyze()
        elif choice == '4':
            export_transactions_to_csv()
        elif choice == '5':
            import_transactions_from_csv()
        elif choice == '6':
            show_spending_by_category()
        elif choice == '7':
            search_assistant.initiate_chat(user_proxy, message="Please enter the SQL query you'd like to execute. Remember that this option allows bulk operations, including edits or deletions.")
        elif choice == '8':
            print("Thank you for using the Personal Finance Management System. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()