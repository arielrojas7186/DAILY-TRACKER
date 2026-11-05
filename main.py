from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from repositories import * 

from routers import router

app = FastAPI(title="daily")

# The browser blocks React (another port) from calling this API
# unless the API says "this origin is allowed".


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

app.get("/menu/questions")
def get_questions():
    ...


app.post("/menu/enter_questions/{questions}")
def insert_questions(questions : dict  ):
    ...
