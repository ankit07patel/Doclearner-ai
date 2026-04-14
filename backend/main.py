import os
import uuid
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from auth import hash_password, verify_password, create_access_token, decode_token
from database import users_collection, documents_collection
from rag import ingest_document, query_document

app = FastAPI(title="Doclearner AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

UPLOAD_DIR = "./uploads"

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ChatRequest(BaseModel):
    doc_id: str
    question: str


# --- Auth Routes ---

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


# --- Document Routes ---

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    email = decode_token(credentials.credentials)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Save file to uploads folder
    doc_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}.pdf")

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Ingest into ChromaDB
    chunk_count = ingest_document(file_path, doc_id)

    # Save document info to MongoDB
    await documents_collection.insert_one({
        "doc_id": doc_id,
        "filename": file.filename,
        "email": email,
        "chunk_count": chunk_count,
        "created_at": str(__import__("datetime").datetime.utcnow())
    })

    return {
        "doc_id": doc_id,
        "filename": file.filename,
        "chunks": chunk_count,
        "message": "PDF uploaded and processed successfully"
    }


@app.get("/documents")
async def get_documents(credentials: HTTPAuthorizationCredentials = Depends(security)):
    email = decode_token(credentials.credentials)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    docs = await documents_collection.find({"email": email}).to_list(100)
    for doc in docs:
        doc.pop("_id", None)

    return {"documents": docs}


# --- Chat Route ---

@app.post("/chat")
async def chat(
    req: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    email = decode_token(credentials.credentials)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Check document belongs to user
    doc = await documents_collection.find_one({
        "doc_id": req.doc_id,
        "email": email
    })
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get relevant context from ChromaDB
    context = query_document(req.doc_id, req.question)

    return {
        "question": req.question,
        "context": context,
        "message": "Context retrieved successfully"
    }