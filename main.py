import os
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from .db import SessionLocal, Prospect, init_db
from .schemas import ProspectIn, ProspectOut, BoardMeta

BOARD_LABEL = os.environ.get("BOARD_LABEL", "Gavin's NFL Draft Big Board")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")  # set this in production; writes are blocked without it

# Comma-separated list of origins allowed to call this API, e.g. your Netlify/GitHub Pages URL.
# "*" (the default) is fine for a public read-only board, but set this explicitly in production.
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")

app = FastAPI(title="Draft Board API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_admin(x_admin_token: str | None = Header(default=None)):
    if not ADMIN_TOKEN:
        raise HTTPException(500, "ADMIN_TOKEN is not configured on the server")
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(401, "Invalid or missing X-Admin-Token header")


@app.get("/api/draft-board", response_model=list[ProspectOut])
def list_prospects(db: Session = Depends(get_db)):
    return db.query(Prospect).order_by(Prospect.rank.asc()).all()


@app.get("/api/draft-board/meta", response_model=BoardMeta)
def board_meta(db: Session = Depends(get_db)):
    count = db.query(func.count(Prospect.id)).scalar() or 0
    latest = db.query(func.max(Prospect.updated_at)).scalar()
    return BoardMeta(label=BOARD_LABEL, updated=latest.strftime("%m/%d/%Y") if latest else None, count=count)


@app.post("/api/draft-board", response_model=ProspectOut, dependencies=[Depends(require_admin)])
def create_prospect(payload: ProspectIn, db: Session = Depends(get_db)):
    row = Prospect(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.put("/api/draft-board/{prospect_id}", response_model=ProspectOut, dependencies=[Depends(require_admin)])
def update_prospect(prospect_id: int, payload: ProspectIn, db: Session = Depends(get_db)):
    row = db.get(Prospect, prospect_id)
    if not row:
        raise HTTPException(404, "Prospect not found")
    for field, value in payload.model_dump().items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row


@app.delete("/api/draft-board/{prospect_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_prospect(prospect_id: int, db: Session = Depends(get_db)):
    row = db.get(Prospect, prospect_id)
    if not row:
        raise HTTPException(404, "Prospect not found")
    db.delete(row)
    db.commit()


@app.get("/")
def root():
    return {"ok": True, "see": "/api/draft-board and /api/draft-board/meta"}
