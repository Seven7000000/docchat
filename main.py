from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import PyPDF2
import io
import uuid
import os

app = FastAPI(title="DocChat AI")

# In-memory document store
documents: dict[str, str] = {}

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
MODEL = "anthropic/claude-sonnet-4-20250514"


class ChatRequest(BaseModel):
    doc_id: str
    question: str
    history: list[dict] = []


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    try:
        content = await file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""

        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")

        doc_id = str(uuid.uuid4())
        # Store up to 50k chars
        documents[doc_id] = text[:50000]

        return {
            "doc_id": doc_id,
            "filename": file.filename,
            "pages": len(pdf_reader.pages),
            "chars": len(documents[doc_id]),
        }
    except PyPDF2.errors.PdfReadError:
        raise HTTPException(status_code=400, detail="Invalid or corrupted PDF file")


@app.post("/chat")
async def chat(req: ChatRequest):
    if req.doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found. Please upload again.")

    doc_text = documents[req.doc_id]

    system_prompt = (
        "You are DocChat AI, an expert document analyst. "
        "Answer the user's question based ONLY on the provided document content. "
        "If the answer is not in the document, say so clearly. "
        "Be concise but thorough. Use markdown formatting when helpful.\n\n"
        f"--- DOCUMENT CONTENT ---\n{doc_text}\n--- END DOCUMENT ---"
    )

    messages = [{"role": "system", "content": system_prompt}]
    for msg in req.history[-10:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": req.question})

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"model": MODEL, "messages": messages, "max_tokens": 2000},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
        return {"answer": answer}
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="AI request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")
