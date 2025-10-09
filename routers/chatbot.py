from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services import chatbot as chatbot_service

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    message: str

@router.post("/chat")
def chat(request: ChatRequest):
    try:
        response = chatbot_service.get_chatbot_response(request.user_id, request.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
