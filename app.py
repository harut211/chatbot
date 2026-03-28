from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from service.prompt import GeminiService

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
try:
    ai_service = GeminiService()
except Exception as exc:
    ai_service = None
    startup_error = str(exc)
else:
    startup_error = ""


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")




@app.post("/chat")
def chat(req: ChatRequest):
    if ai_service is None:
        raise HTTPException(status_code=500, detail=f"Ծառայությունը հասանելի չէ: {startup_error}")

    try:
        response = ai_service.generate_response(req.message)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Պատասխան գեներացնելը ձախողվել է: {exc}") from exc

    return {"response": response}