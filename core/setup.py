import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
import json

# Explicitly load .env file from the project root to ensure it's found.
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
else:
    print("⚠️ .env file not found. Firebase initialization will likely fail.")

def initialize_firebase():
    """
    Initializes the Firebase Admin SDK from environment variables.
    Ensures initialization happens only once.
    """
    if firebase_admin._apps:
        return firestore.client()

    try:
        raw_pk = os.environ["FIREBASE_PRIVATE_KEY"].strip()
        if raw_pk.startswith('"') and raw_pk.endswith('"'):
            raw_pk = raw_pk[1:-1]
        private_key = raw_pk.replace('\\n', '\n')

        cred_dict = json.loads(os.environ.get("FIREBASE_PRIVATE_KEY"))
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase connection successful.")
        return firestore.client()
    except Exception as e:
        print(f"🔥 Error initializing Firebase: {e}")
        return None

# Initialize the database connection for the application
db = initialize_firebase()
