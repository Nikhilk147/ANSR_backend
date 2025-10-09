import re
from datetime import datetime
import json

# Assuming these services are in the same directory or accessible through the python path
from services.alert import limit_checker
from services.anomaly import detect_amount_anomalies_by_category, detect_time_anomalies

# Placeholder for a function to get historical transactions for a user.
# In a real application, this would fetch data from Firebase/DB.
def get_user_transactions(user_id):
    # This is a placeholder. In a real implementation, you would fetch
    # transactions for the given user_id from your database (e.g., Firebase).
    # For now, returning an empty list.
    return []

def clean_raw_data(raw_data_string):
    """
    Cleans a raw data string and returns a dictionary with the cleaned data.

    Args:
        raw_data_string: A string in the format "ID, timestamp, application, sender (optional), exact message"

    Returns:
        A dictionary containing the cleaned data, or None if the format is invalid.
    """
    parts = [p.strip() for p in raw_data_string.split(',', 4)]
    if len(parts) < 4:
        return None  # Invalid format

    raw_id, raw_timestamp, application, raw_message = None, None, None, None
    raw_sender = None

    if len(parts) == 5:
        raw_id, raw_timestamp, application, raw_sender, raw_message = parts
    else:
        raw_id, raw_timestamp, application, raw_message = parts

    # 1. Parse timestamp
    try:
        # Assuming timestamp is in a recognizable format, e.g., ISO 8601
        dt_object = datetime.fromisoformat(raw_timestamp)
        timestamp = {
            "year": dt_object.year,
            "month": dt_object.month,
            "day": dt_object.day,
            "hour": dt_object.hour,
        }
    except ValueError:
        # Handle other potential timestamp formats or errors
        timestamp = {"year": None, "month": None, "day": None, "hour": None}

    # 2. Extract sender
    sender = raw_sender if raw_sender else "Unknown"

    # 3. Parse the message for payment details
    payment_method = "Unknown"
    payment_type = "Unknown"
    amount = None
    category = "Uncategorized"  # Default category
    message = raw_message

    # Simple regex to find amount (assuming format like $123.45 or 123.45)
    amount_match = re.search(r'(\d+\.?\d*)', raw_message)
    if amount_match:
        amount = float(amount_match.group(1))

    # Determine payment method
    if "credit" in raw_message.lower():
        payment_method = "credit"
    elif "upi" in raw_message.lower():
        payment_method = "UPI"

    # Determine payment type
    if "incoming" in raw_message.lower() or "received" in raw_message.lower():
        payment_type = "incoming"
    elif "outgoing" in raw_message.lower() or "sent" in raw_message.lower():
        payment_type = "outgoing"

    cleaned_data = {
        "ID": raw_id,
        "timestamp": timestamp,
        "sender": sender,
        "payment_method": payment_method,
        "payment_type": payment_type,
        "Amount": amount, # Changed to Amount to match anomaly detection script
        "Category": category, # Changed to Category to match anomaly detection script
        "message": message,
    }

    return cleaned_data

def process_transaction(raw_data_string):
    """
    Processes a raw transaction string, cleans it, checks for alerts and anomalies,
    and prepares it for storage.

    Args:
        raw_data_string: The raw transaction data.

    Returns:
        A dictionary with the processed data and any generated messages.
    """
    cleaned_data = clean_raw_data(raw_data_string)
    if not cleaned_data:
        return {"error": "Invalid raw data format"}

    user_id = cleaned_data.get("ID")
    alert_message = "No alerts"
    anomaly_message = "No anomalies detected"

    # 1. Check for spending limit alerts
    if user_id:
        alert_message = limit_checker(user_id)

    # 2. Perform anomaly detection
    if user_id:
        # Fetch historical transactions for the user to build context for anomaly detection
        historical_transactions = get_user_transactions(user_id)
        all_transactions = historical_transactions + [cleaned_data]

        high_amount_ids = detect_amount_anomalies_by_category(all_transactions)
        unusual_time_ids = detect_time_anomalies(all_transactions)

        reasons = []
        if cleaned_data['ID'] in high_amount_ids:
            reasons.append(f"Amount is significantly higher than other '{cleaned_data.get('Category', 'N/A')}' expenses.")
        if cleaned_data['ID'] in unusual_time_ids:
            reasons.append("Transaction occurred at an unusual time (late night).")

        if reasons:
            anomaly_message = "Potential anomaly detected: " + " ".join(reasons)


    # 3. Save to Firebase (placeholder)
    # In a real implementation, you would have your Firebase logic here.
    # For example:
    # from services.firebase_client import db
    # db.collection('transactions').document(cleaned_data['ID']).set(cleaned_data)
    firebase_save_status = "Data prepared for Firebase."

    return {
        "cleaned_data": cleaned_data,
        "alert_message": alert_message,
        "anomaly_message": anomaly_message,
        "firebase_status": firebase_save_status
    }


if __name__ == '__main__':
    # Example Usage
    raw_data_1 = "user123, 2025-10-09T14:30:00, MyApp, John Doe, incoming credit payment of 50.00 for groceries"
    raw_data_2 = "user123, 2025-10-09T23:00:00, YourApp, , outgoing upi payment of 2500.50 for rent" # high amount but recurring
    raw_data_3 = "user456, 2025-10-10T02:00:00, AnotherApp, Jane Smith, sent 100.00 via upi" # unusual time

    processed_1 = process_transaction(raw_data_1)
    processed_2 = process_transaction(raw_data_2)
    processed_3 = process_transaction(raw_data_3)

    print(json.dumps(processed_1, indent=2))
    print(json.dumps(processed_2, indent=2))
    print(json.dumps(processed_3, indent=2))