from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from connection_db import initialize_connection

router = APIRouter(prefix="/menu")


class Entry(BaseModel):
    question_id: int
    score: float = Field(ge=0, le=1)  # FastAPI rejects anything else with 422


# TEMPORARY: SQL lives here only to get the frontend working.
# Step 2 moves it into repositories.py / services.py.


@router.get("/questions")
def list_questions():
    conn = initialize_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("select id, question from questions order by id")
            return [{"question_id": i, "question": q} for i, q in cur.fetchall()]
    finally:
        conn.close()


@router.post("/questions/insert")
def insert_scores(entries: list[Entry]):
    # 1) Validate EVERYTHING before touching the DB.
    if not entries:
        raise HTTPException(status_code=400, detail="Send at least one score")
    ids = [e.question_id for e in entries]
    if len(set(ids)) != len(ids):
        raise HTTPException(status_code=400, detail="Repeated question_id in request")

    conn = initialize_connection()
    try:
        # 2) `with conn` = one transaction: commit if OK, rollback if anything raises.
        with conn:
            with conn.cursor() as cur:
                cur.execute("select id from questions where id = any(%s)", (ids,))
                unknown = set(ids) - {row[0] for row in cur.fetchall()}
                if unknown:
                    raise HTTPException(
                        status_code=400, detail=f"Unknown question ids: {sorted(unknown)}"
                    )
                cur.executemany(
                    "insert into daily_tracker (date, question_id, score) values (%s, %s, %s)",
                    [(date.today(), e.question_id, e.score) for e in entries],
                )
        return {"saved": len(entries)}
    finally:
        conn.close()
