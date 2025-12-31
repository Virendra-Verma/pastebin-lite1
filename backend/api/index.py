from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import time
import uuid
from typing import Optional
from database import get_db, init_db, Paste

app = FastAPI(title="Pastebin Lite API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    print("Starting up FastAPI app...")
    init_db()
    print("Database initialized successfully!")

class PasteCreate(BaseModel):
    content: str
    ttl_seconds: Optional[int] = None
    max_views: Optional[int] = None

class PasteResponse(BaseModel):
    id: str
    url: str

@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": int(time.time() * 1000)}

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "message": "Pastebin Lite API",
        "endpoints": {
            "health": "/healthz",
            "create_paste": "POST /pastes",
            "get_paste": "GET /pastes/{id}",
            "view_paste": "GET /p/{id}"
        }
    }

@app.get("/pastes/{paste_id}")
async def get_paste(paste_id: str, db: Session = Depends(get_db)):
    """Get paste content as JSON"""
    current_time = int(time.time() * 1000)
    
    paste = db.query(Paste).filter(Paste.id == paste_id).first()
    
    if not paste:
        raise HTTPException(status_code=404, detail="Paste not found")
    
    # Check expiration
    if paste.expires_at and current_time > paste.expires_at:
        raise HTTPException(status_code=404, detail="Paste expired")
    
    # Check max views
    if paste.max_views and paste.views >= paste.max_views:
        raise HTTPException(status_code=404, detail="Paste view limit reached")
    
    # Increment view count
    paste.views += 1
    db.commit()
    
    return {"content": paste.content}

@app.get("/p/{paste_id}", response_class=HTMLResponse)
async def view_paste(paste_id: str, db: Session = Depends(get_db)):
    """View paste as HTML page"""
    current_time = int(time.time() * 1000)
    
    paste = db.query(Paste).filter(Paste.id == paste_id).first()
    
    if not paste:
        return HTMLResponse(content="<h1>Paste not found</h1>", status_code=404)
    
    # Check expiration
    if paste.expires_at and current_time > paste.expires_at:
        return HTMLResponse(content="<h1>Paste expired</h1>", status_code=404)
    
    # Check max views
    if paste.max_views and paste.views >= paste.max_views:
        return HTMLResponse(content="<h1>Paste view limit reached</h1>", status_code=404)
    
    # Increment view count
    paste.views += 1
    db.commit()
    
    # Escape HTML for safe display
    safe_content = paste.content.replace("<", "&lt;").replace(">", "&gt;")
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Paste {paste_id}</title>
        <style>
            body {{ font-family: monospace; margin: 20px; }}
            pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; white-space: pre-wrap; }}
            .meta {{ color: #666; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="meta">Paste ID: {paste_id}</div>
        <pre>{safe_content}</pre>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html)

@app.post("/pastes", response_model=PasteResponse)
async def create_paste(paste: PasteCreate, db: Session = Depends(get_db)):
    """Create a new paste"""
    try:
        print(f"Creating paste with content length: {len(paste.content)}")
        
        if not paste.content.strip():
            raise HTTPException(status_code=400, detail="Content cannot be empty")
        
        # Calculate expiration time
        expires_at = None
        if paste.ttl_seconds:
            expires_at = int(time.time() * 1000) + (paste.ttl_seconds * 1000)
        
        # Generate unique ID
        paste_id = uuid.uuid4().hex[:8]
        
        # Ensure ID is unique
        while db.query(Paste).filter(Paste.id == paste_id).first():
            paste_id = uuid.uuid4().hex[:8]
        
        # Create new paste record
        new_paste = Paste(
            id=paste_id,
            content=paste.content,
            expires_at=expires_at,
            max_views=paste.max_views,
            views=0,
            created_at=int(time.time() * 1000)
        )
        
        db.add(new_paste)
        db.commit()
        db.refresh(new_paste)
        
        print(f"Successfully created paste with ID: {paste_id}")
        
        return {
            "id": paste_id,
            "url": f"/p/{paste_id}"
        }
    except Exception as e:
        print(f"Error creating paste: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
