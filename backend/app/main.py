"""
Entry point. Right now this only proves the backend boots, connects to the
DB (SQLite by default), and can create + retrieve a Document row. No agents,
no LLM calls, no retrieval yet — that comes in later steps, once this
foundation is confirmed working.
"""
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import init_db, get_db
from app.db.models import Document

app = FastAPI(title="Titan - Compliance Document Intelligence")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "env": settings.env,
        "database": "sqlite" if settings.is_sqlite else "postgres",
    }


class DocumentIn(BaseModel):
    filename: str
    raw_text: str


class DocumentOut(BaseModel):
    id: int
    filename: str
    status: str

    class Config:
        from_attributes = True


@app.post("/documents", response_model=DocumentOut)
def create_document(payload: DocumentIn, db: Session = Depends(get_db)):
    doc = Document(filename=payload.filename, raw_text=payload.raw_text, status="pending")
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@app.get("/documents", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.id.desc()).all()


@app.get("/documents/{document_id}", response_model=DocumentOut)
def get_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if doc is None:
        return {"error": "not found"}
    return doc