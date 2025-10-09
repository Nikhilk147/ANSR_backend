from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import pandas as pd

from services import visualization as viz_service
from services.firebase import get_firestore_client

router = APIRouter()

@router.get("/visualize/{chart_type}", tags=["Visualization"])
async def get_visualization(chart_type: str, user_id: str):
    """
    Generates a visualization of the user's transaction data.
    """
    db = get_firestore_client()
    transactions_ref = db.collection('Expenses').document(user_id).collection('transactions')
    docs = transactions_ref.stream()

    transactions = [doc.to_dict() for doc in docs]

    if not transactions:
        raise HTTPException(status_code=404, detail="No transaction data found for this user.")

    df = pd.DataFrame(transactions)

    if chart_type == "monthly_expenses_bar":
        image_buf = viz_service.visualize_monthly_expenses_bar(df)
    elif chart_type == "daily_expenses_line":
        image_buf = viz_service.visualize_daily_expenses_line(df)
    elif chart_type == "category_pie":
        image_buf = viz_service.visualize_category_pie(df)
    elif chart_type == "payment_method_pie":
        image_buf = viz_service.visualize_payment_method_pie(df)
    else:
        raise HTTPException(status_code=400, detail="Invalid chart type specified.")

    if image_buf is None:
        raise HTTPException(status_code=404, detail="No data available for the specified chart type.")

    return StreamingResponse(image_buf, media_type="image/png")
