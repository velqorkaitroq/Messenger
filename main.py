from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Replacing the database for now
users: dict[str, dict] = {}

class RegisterRequest(BaseModel):
    login: str

class UserResponse(BaseModel):
    id: str
    login: str
    created_at: str

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/user/register", response_model=UserResponse)
def register(data: RegisterRequest):
    login = data.login.strip().lower()

    if not login:
        raise HTTPException(status_code=400, detail="The username cannot be empty")

    for user in users.values():
        if user["login"] == login:
            raise HTTPException(status_code=409, detail="This username already exists")

    user_id = str(uuid4())
    user = {
        "id": user_id,
        "login": login,
        "created_at": datetime.utcnow().isoformat(),
    }
    users[user_id] = user
    return user


@app.get("/user/list", response_model=list[UserResponse])
def get_all_users():
    return list(users.values())


@app.get("/user/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    user = users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user