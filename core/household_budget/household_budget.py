'''
Household Budget Management
Main functions:
- Create a household budget based on user input and financial data.
- Track and analyze spending patterns.
- Generate reports on budget performance.
using IA to analyze receipts to track spending and categorize expenses.
- By uploading weither a picture of the receipt or a PDF of the receipt, the AI can extract the
relevant information and update the household budget accordingly.
- Analyze the stored data to provide insights on spending patterns and suggest ways to optimize the budget, also generates reports on budget performance.
'''

import core.global_functions as global_functions
import providers.openai_parts.openai_functions as openai_functions
import providers.google_parts.drive_google as drive_google


SQL_DB_NAME = "household_budget.db"
# drive_google.create_database(SQL_DB_NAME)





if __name__ == "__main__":
    pass
