from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from parser import parse_pdf_resume
from keywords import extract_keywords
from matcher import classify_and_score

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for MVP; tighten later
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/analyze")
async def analyze(resume_file: UploadFile = File(...),
                  job_text: str = Form(...),
                  max_k: int = Form(10)):
    pdf_bytes = await resume_file.read()
    parsed = parse_pdf_resume(pdf_bytes, filename=resume_file.filename)

    keywords = extract_keywords(job_text, max_k=max_k)
    result = classify_and_score(
        keywords=keywords,
        resume_skills=parsed.get("skills", []),
        resume_text=parsed.get("text", "")
    )
    return {
        "contact": parsed.get("contact", {}),
        "keywords": keywords,
        **result
    }
