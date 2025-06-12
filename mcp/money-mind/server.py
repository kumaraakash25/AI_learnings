import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("money-mind")

# ---------------------------------------------------------------------
# Simulated Data Stores (Replace with DB/API in production)
# ---------------------------------------------------------------------

ACCOUNTS = {
    "checking": {"balance": 1500.00},
    "savings": {"balance": 5000.00},
    "credit_card": {"balance": -800.00}  # Negative = money owed
}

TRANSACTIONS = [
    {"date": "2025-06-01", "category": "restaurants", "amount": 75.50, "description": "Dinner with friends"},
    {"date": "2025-06-03", "category": "groceries", "amount": 120.00, "description": "Weekly groceries"},
    {"date": "2025-06-05", "category": "restaurants", "amount": 45.20, "description": "Lunch at cafe"},
    {"date": "2025-06-07", "category": "transport", "amount": 30.00, "description": "Fuel"},
    {"date": "2025-06-10", "category": "subscriptions", "amount": 15.00, "description": "Netflix monthly"},
    {"date": "2025-06-11", "category": "restaurants", "amount": 60.10, "description": "Takeout"},
    {"date": "2025-06-12", "category": "utilities", "amount": 85.00, "description": "Electricity bill"},
    {"date": "2025-06-12", "category": "subscriptions", "amount": 9.99, "description": "Spotify Premium"},
    {"date": "2025-06-01", "category": "income", "amount": 3000.00, "description": "Salary"},
    {"date": "2025-05-15", "category": "subscriptions", "amount": 15.00, "description": "Netflix (previous month)"},
    {"date": "2025-05-15", "category": "subscriptions", "amount": 9.00, "description": "Spotify Premium (previous month)"},
]

# ---------------------------------------------------------------------
# Resource: Static Application Config
# ---------------------------------------------------------------------

@mcp.resource("config://app")
def get_config() -> str:
    """
    Provides static application configuration (simulating config from a file or secret store).
    """
    return """
    {
      "env": "production",
      "retry_limit": 3,
      "alert_threshold": 80
    }
    """

# ---------------------------------------------------------------------
# Tool: Track Spending by Category
# ---------------------------------------------------------------------

@mcp.tool()
def get_category_spending(category_name: str, period: str = "this month") -> str:
    """
    Calculates total spending in a specific category during the specified period.
    Currently supports 'this month' based on transaction dates.
    """
    total_spent = 0.0
    today = datetime.datetime.now()
    for tx in TRANSACTIONS:
        try:
            tx_date = datetime.datetime.strptime(tx["date"], "%Y-%m-%d")
        except ValueError:
            continue  # Skip malformed dates

        if (
            period == "this month" and
            tx_date.month == today.month and
            tx_date.year == today.year and
            tx["category"].lower() == category_name.lower() and
            tx["amount"] > 0
        ):
            total_spent += tx["amount"]

    return f"You've spent ₹{total_spent:.2f} on {category_name} {period}."

# ---------------------------------------------------------------------
# Tool: Transfer Funds Between Accounts
# ---------------------------------------------------------------------

@mcp.tool()
def transfer_funds(from_account: str, to_account: str, amount: float) -> str:
    """
    Transfers a specified amount between accounts. Returns updated balances.
    """
    from_acc = from_account.lower()
    to_acc = to_account.lower()

    if from_acc not in ACCOUNTS or to_acc not in ACCOUNTS:
        return "❌ Error: One or both account names are invalid."
    if amount <= 0:
        return "❌ Error: Transfer amount must be positive."
    if ACCOUNTS[from_acc]["balance"] < amount:
        return f"❌ Error: Insufficient funds in {from_account} (Available: ₹{ACCOUNTS[from_acc]['balance']:.2f})."

    ACCOUNTS[from_acc]["balance"] -= amount
    ACCOUNTS[to_acc]["balance"] += amount

    return (
        f"✅ Transferred ₹{amount:.2f} from {from_account} to {to_account}.\n"
        f"Updated balances:\n"
        f"- {from_account.capitalize()}: ₹{ACCOUNTS[from_acc]['balance']:.2f}\n"
        f"- {to_account.capitalize()}: ₹{ACCOUNTS[to_acc]['balance']:.2f}"
    )

# ---------------------------------------------------------------------
# Tool: Check Account Balance(s)
# ---------------------------------------------------------------------

@mcp.tool()
def get_account_balance(account_name: str) -> str:
    """
    Retrieves current balance of the specified account, or all if 'all' is passed.
    """
    name = account_name.lower()
    if name == "all":
        return "Current balances:\n" + "\n".join(
            f"- {acc.capitalize()}: ₹{info['balance']:.2f}" for acc, info in ACCOUNTS.items()
        )
    elif name in ACCOUNTS:
        balance = ACCOUNTS[name]["balance"]
        return f"Your {account_name.capitalize()} balance is ₹{balance:.2f}."
    else:
        return f"❌ Unknown account: '{account_name}'. Valid accounts: {', '.join(ACCOUNTS.keys())}."

# ---------------------------------------------------------------------
# Prompt Tool: Personalized Financial Advice
# ---------------------------------------------------------------------

@mcp.prompt()
def financial_advice(goal: str, income: str, expenses: str, risk_profile: str) -> str:
    """
    Generates tailored financial advice using LLM based on client profile and goals.
    """
    return (
        f"You are a seasoned financial advisor.\n"
        f"Your client has provided the following information:\n\n"
        f"- Goal: {goal}\n"
        f"- Monthly Income: {income}\n"
        f"- Monthly Expenses: {expenses}\n"
        f"- Risk Profile: {risk_profile}\n\n"
        f"Please generate a financial plan including:\n"
        f"1. Savings recommendations\n"
        f"2. Investment options\n"
        f"3. Risk mitigation strategies\n"
        f"4. Monthly budgeting tips"
    )

# ---------------------------------------------------------------------
# Start the MCP Server
# ---------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
