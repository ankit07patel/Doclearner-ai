from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from auth import (
    fake_users_db, hash_password, verify_password,
    create_access_token, decode_token
)

app = FastAPI(title="Doclearner AI")

# This allows your React frontend to talk to this server later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# These are the shapes of data we accept
class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str


@app.get("/health")
def health():
    return {"status": "ok", "message": "DocuChat AI is running"}


@app.post("/register")
def register(req: RegisterRequest):
    if req.email in fake_users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    fake_users_db[req.email] = {
        "email": req.email,
        "password": hash_password(req.password)
    }
    
    token = create_access_token({"sub": req.email})
    return {"token": token, "email": req.email, "message": "Registered successfully"}


@app.post("/login")
def login(req: LoginRequest):
    user = fake_users_db.get(req.email)
    
    if not user or not verify_password(req.password, user["password"]):
        raise HTTPException(status_code=401, detail="Wrong email or password")
    
    token = create_access_token({"sub": req.email})
    return {"token": token, "email": req.email, "message": "Login successful"}


@app.get("/me")
def get_me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    email = decode_token(credentials.credentials)
    
    if not email or email not in fake_users_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"email": email, "message": "Token is valid"}