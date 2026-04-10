from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from auth import hash_password, verify_password, create_access_token, decode_token
from database import users_collection

app = FastAPI(title="Doclearner AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str


@app.get("/health")
async def health():
    return {"status": "ok", "message": "Doclearner AI is running"}


@app.post("/register")
async def register(req: RegisterRequest):
    existing = await users_collection.find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    await users_collection.insert_one({
        "email": req.email,
        "password": hash_password(req.password),
        "created_at": str(__import__("datetime").datetime.utcnow())
    })

    token = create_access_token({"sub": req.email})
    return {"token": token, "email": req.email, "message": "Registered successfully"}


@app.post("/login")
async def login(req: LoginRequest):
    user = await users_collection.find_one({"email": req.email})

    if not user or not verify_password(req.password, user["password"]):
        raise HTTPException(status_code=401, detail="Wrong email or password")

    token = create_access_token({"sub": req.email})
    return {"token": token, "email": req.email, "message": "Login successful"}


@app.get("/me")
async def get_me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    email = decode_token(credentials.credentials)

    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return {"email": email, "message": "Token is valid"}