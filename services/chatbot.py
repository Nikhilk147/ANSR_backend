from services.firebase import get_firestore_client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import os

def get_chatbot_response(user_id: str, message: str):
    """
    Handles the chatbot conversation logic.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=os.getenv("GEMINI_API_KEY"))

    db = get_firestore_client()
    chat_ref = db.collection("chats").document(user_id)
    chat_history = chat_ref.get()

    if chat_history.exists:
        messages_dict = chat_history.to_dict().get("messages", [])
        messages = []
        for msg in messages_dict:
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                messages.append(AIMessage(content=msg['content']))
    else:
        messages = []

    # Add the new user message to the history
    messages.append(HumanMessage(content=message))

    # Construct the prompt for Gemini
    prompt = [
        SystemMessage(content="""You are FinSight, a friendly and intelligent financial assistant. Your purpose is to help users understand their spending and make smarter financial decisions. You can answer questions about the user's transactions, subscriptions, budgets, and spending patterns. You can also provide insights and predictions based on their financial activity.

You have access to the following information about the user's financial data:

**Transactions:**
*   Amount, date, and time
*   Sender/merchant name
*   Payment method (Credit, Debit, UPI)
*   Category (e.g., Food, Travel)
*   Anomalous transaction flags

**Budgets and Limits:**
*   Daily, weekly, monthly, and yearly spending limits

**Pending Payments:**
*   Money to give or take from others

**Summaries:**
*   Daily, weekly, monthly, and yearly income, expenses, and cash flow

**App Features:**
*   Subscription and regular payment detection
*   Smart alerts and fraud anomaly detection
*   Refund and income tracking
*   Bill and cashflow prediction
*   Spending summaries
*   Pending payments tracking

**Your role is to answer questions and provide guidance related to these features and data. If a user asks a question that is not related to their finances or the FinSight app, you must politely decline and steer the conversation back to your purpose. For example, if they ask about the weather or a movie, you should say something like: 'I am a financial assistant and can only answer questions about your finances and the FinSight app. How can I help you with your spending today?'"""),
    ]
    prompt.extend(messages)

    response = llm.invoke(prompt)

    # Add the bot's response to the history
    messages.append(response)

    # Save the updated chat history to Firestore
    messages_to_save = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            messages_to_save.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            messages_to_save.append({"role": "assistant", "content": msg.content})

    chat_ref.set({"messages": messages_to_save})

    return response.content
