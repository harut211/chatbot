from fastapi import FastAPI
from pydantic import BaseModel
from service.prompt import GeminiService

app = FastAPI()
ai_service = GeminiService()


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(req: ChatRequest):
    response = ai_service.generate_response(req.message)
    return {"response": response}