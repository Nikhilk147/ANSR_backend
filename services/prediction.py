import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

def get_spending_prediction(user_id: str, timeframe: str):
    """
    Predicts future expenses based on historical data.

    Args:
        user_id (str): The ID of the user.
        timeframe (str): The prediction timeframe ('daily', 'weekly', or 'monthly').

    Returns:
        dict: A dictionary containing the predicted expenses, or a message if there's not enough data.
    """
    try:
        db = firestore.client()
        collection_ref = db.collection('Expense_tracker').document('Tracker').collection('Tracker')
        
        # Fetch last 90 days of transactions for the user
        ninety_days_ago = datetime.now() - timedelta(days=90)
        query = collection_ref.where('user_id', '==', user_id).where('timestamp', '>=', ninety_days_ago)
        docs = query.stream()

        transactions = [doc.to_dict() for doc in docs]

        if len(transactions) < 15:
            return {"message": "Not enough data for a reliable prediction."}

        # Separate expenses and income
        expenses = [tx for tx in transactions if tx.get('payment_type') == 'outgoing']
        
        if not expenses:
            return {"message": "No expense data available for prediction."}

        # Group expenses by day
        daily_expenses = defaultdict(float)
        for expense in expenses:
            if isinstance(expense['timestamp'], str):
                expense_date = datetime.fromisoformat(expense['timestamp']).date()
            else:
                expense_date = expense['timestamp'].date()
            daily_expenses[expense_date] += expense['amount']

        if not daily_expenses:
            return {"message": "Not enough daily expense data for prediction."}
            
        # Calculate average daily expense
        avg_daily_expense = sum(daily_expenses.values()) / len(daily_expenses)

        # Trend calculation
        # Compare the average spending of the last 30 days with the average spending of the 30 days before that.
        last_30_days_expenses = [v for k, v in daily_expenses.items() if k >= (datetime.now() - timedelta(days=30)).date()]
        previous_30_days_expenses = [v for k, v in daily_expenses.items() if (datetime.now() - timedelta(days=60)).date() <= k < (datetime.now() - timedelta(days=30)).date()]

        avg_last_30_days = sum(last_30_days_expenses) / len(last_30_days_expenses) if last_30_days_expenses else 0
        avg_previous_30_days = sum(previous_30_days_expenses) / len(previous_30_days_expenses) if previous_30_days_expenses else 0

        if avg_previous_30_days > 0:
            trend = ((avg_last_30_days - avg_previous_30_days) / avg_previous_30_days) * 100
        else:
            trend = 0


        if timeframe == 'daily':
            prediction = avg_daily_expense
        elif timeframe == 'weekly':
            prediction = avg_daily_expense * 7
        elif timeframe == 'monthly':
            prediction = avg_daily_expense * 30
        else:
            return {"message": "Invalid timeframe specified. Use 'daily', 'weekly', or 'monthly'."}

        return {"predicted_expense": round(prediction, 2), "trend": round(trend,2)}

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"message": "An error occurred during prediction."}

def get_cashflow_prediction(user_id: str, timeframe: str):
    """
    Predicts future cashflow based on historical data.

    Args:
        user_id (str): The ID of the user.
        timeframe (str): The prediction timeframe ('daily', 'weekly', or 'monthly').

    Returns:
        dict: A dictionary containing the predicted cashflow, or a message if there's not enough data.
    """
    try:
        db = firestore.client()
        collection_ref = db.collection('Expense_tracker').document('Tracker').collection('Tracker')
        
        # Fetch last 90 days of transactions for the user
        ninety_days_ago = datetime.now() - timedelta(days=90)
        query = collection_ref.where('user_id', '==', user_id).where('timestamp', '>=', ninety_days_ago)
        docs = query.stream()

        transactions = [doc.to_dict() for doc in docs]

        if len(transactions) < 15:
            return {"message": "Not enough data for a reliable prediction."}

        # Separate expenses and income
        expenses = [tx for tx in transactions if tx.get('payment_type') == 'outgoing']
        income = [tx for tx in transactions if tx.get('payment_type') == 'incoming']
        
        if not expenses and not income:
            return {"message": "No transaction data available for prediction."}

        # Group expenses by day
        daily_expenses = defaultdict(float)
        for expense in expenses:
            if isinstance(expense['timestamp'], str):
                expense_date = datetime.fromisoformat(expense['timestamp']).date()
            else:
                expense_date = expense['timestamp'].date()
            daily_expenses[expense_date] += expense['amount']

        # Group income by day
        daily_income = defaultdict(float)
        for inc in income:
            if isinstance(inc['timestamp'], str):
                income_date = datetime.fromisoformat(inc['timestamp']).date()
            else:
                income_date = inc['timestamp'].date()
            daily_income[income_date] += inc['amount']

        # Calculate average daily expense and income
        avg_daily_expense = sum(daily_expenses.values()) / len(daily_expenses) if daily_expenses else 0
        avg_daily_income = sum(daily_income.values()) / len(daily_income) if daily_income else 0

        avg_daily_cashflow = avg_daily_income - avg_daily_expense

        if timeframe == 'daily':
            prediction = avg_daily_cashflow
        elif timeframe == 'weekly':
            prediction = avg_daily_cashflow * 7
        elif timeframe == 'monthly':
            prediction = avg_daily_cashflow * 30
        else:
            return {"message": "Invalid timeframe specified. Use 'daily', 'weekly', or 'monthly'."}

        return {"predicted_cashflow": round(prediction, 2)}

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"message": "An error occurred during prediction."}


def get_daily_spending_trend(user_id: str):
    """
    Gets the daily spending trend for the last 7 days.

    Args:
        user_id (str): The ID of the user.

    Returns:
        dict: A dictionary containing the daily spending trend.
    """
    try:
        db = firestore.client()
        collection_ref = db.collection('Expense_tracker').document('Tracker').collection('Tracker')
        
        # Fetch last 7 days of transactions for the user
        seven_days_ago = datetime.now() - timedelta(days=7)
        query = collection_ref.where('user_id', '==', user_id).where('timestamp', '>=', seven_days_ago).where('payment_type', '==', 'outgoing')
        docs = query.stream()

        transactions = [doc.to_dict() for doc in docs]

        daily_spending = defaultdict(float)
        for tx in transactions:
            if isinstance(tx['timestamp'], str):
                tx_date = datetime.fromisoformat(tx['timestamp']).date()
            else:
                tx_date = tx['timestamp'].date()
            daily_spending[tx_date] += tx['amount']
        
        # Create a list of the last 7 days
        last_7_days = [(datetime.now() - timedelta(days=i)).date() for i in range(7)]
        
        trend_data = {day.strftime("%Y-%m-%d"): daily_spending.get(day, 0) for day in sorted(last_7_days)}

        return {"daily_spending_trend": trend_data}

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"message": "An error occurred while fetching daily trend."}


def get_monthly_spending_trend(user_id: str):
    """
    Gets the monthly spending trend for the last 12 months.

    Args:
        user_id (str): The ID of the user.

    Returns:
        dict: A dictionary containing the monthly spending trend.
    """
    try:
        db = firestore.client()
        collection_ref = db.collection('Expense_tracker').document('Tracker').collection('Tracker')
        
        # Fetch last 12 months of transactions for the user
        twelve_months_ago = datetime.now() - timedelta(days=365)
        query = collection_ref.where('user_id', '==', user_id).where('timestamp', '>=', twelve_months_ago).where('payment_type', '==', 'outgoing')
        docs = query.stream()

        transactions = [doc.to_dict() for doc in docs]

        monthly_spending = defaultdict(float)
        for tx in transactions:
            if isinstance(tx['timestamp'], str):
                tx_date = datetime.fromisoformat(tx['timestamp'])
            else:
                tx_date = tx['timestamp']
            monthly_spending[tx_date.strftime("%Y-%m")] += tx['amount']
        
        # Create a list of the last 12 months
        last_12_months = [(datetime.now() - timedelta(days=30*i)).strftime("%Y-%m") for i in range(12)]
        
        trend_data = {month: monthly_spending.get(month, 0) for month in sorted(last_12_months, reverse=True)}

        return {"monthly_spending_trend": trend_data}

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"message": "An error occurred while fetching monthly trend."}