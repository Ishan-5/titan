"""
Core tables. Kept deliberately small for now — just enough to prove
documents and findings round-trip through the database correctly.

Note on `embedding`: stored as a Text column (JSON-encoded float list) for
now so it works identically on SQLite and Postgres. When we add real vector
search later, Postgres will get a proper `vector` column via a migration,
while SQLite keeps this JSON column and does cosine similarity in Python.
That split lives in vector_adapter.py, not here — this file never needs
to change when that happens.
"""
import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Float
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    raw_text = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="pending")
    # pending -> processing -> done -> failed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    findings = relationship("Finding", back_populates="document")


class PolicyClause(Base):
    __tablename__ = "policy_clauses"

    id = Column(Integer, primary_key=True)
    section = Column(String, nullable=False)        # e.g. "Section 2 - PII Handling"
    clause_number = Column(String, nullable=False)   # e.g. "2.3"
    text = Column(Text, nullable=False)              # the exact clause text, verbatim
    embedding = Column(Text, nullable=True)          # JSON-encoded float list


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    span_start = Column(Integer, nullable=False)
    span_end = Column(Integer, nullable=False)
    flagged_text = Column(Text, nullable=False)

    agent_source = Column(String, nullable=False)  # "pii" | "confidentiality" | "clause_matcher"

    matched_clause_id = Column(Integer, ForeignKey("policy_clauses.id"), nullable=True)
    matched_clause_text = Column(Text, nullable=True)  # denormalized, exact retrieved text

    retrieval_score = Column(Float, nullable=True)
    llm_confidence = Column(String, nullable=True)  # "high" | "medium" | "low"
    reconciliation_status = Column(String, nullable=False, default="pending")
    # pending -> auto_confirmed | needs_review | no_match | approved | rejected

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    document = relationship("Document", back_populates="findings")