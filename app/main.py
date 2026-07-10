import os
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlmodel import SQLModel, Field, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import init_db, get_session
from fastapi.responses import Response
from fastapi import Request

# Define the Database Table Data Model
class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: Optional[str] = None
    completed: bool = Field(default=False)

app = FastAPI(title="Coolify PostgreSQL Stack App", version="1.0.0")

# Enable CORS so your standalone frontend can safely execute cross-origin API calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to specific domains in strict production setups
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def add_csp_header(request: Request, call_next):
    response: Response = await call_next(request)
    # Appends 'unsafe-eval' and 'unsafe-inline' to let Swagger UI and Tailwind scripts initialize smoothly
    response.headers["Content-Security-Policy"] = (
        "default-src 'self' * 'unsafe-inline' 'unsafe-eval'; "
        "script-src 'self' * 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' * 'unsafe-inline';"
    )
    return response
# Automated database bootstrapping hook
@app.on_event("startup")
async def on_startup():
    await init_db()

# CRUD: CREATE (Async)
@app.post("/api/items", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: Item, session: AsyncSession = Depends(get_session)):
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item

# CRUD: READ ALL (Async)
@app.get("/api/items", response_model=List[Item])
async def read_items(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Item))
    return result.scalars().all()

# CRUD: READ SINGLE (Async)
@app.get("/api/items/{item_id}", response_model=Item)
async def read_item(item_id: int, session: AsyncSession = Depends(get_session)):
    item = await session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# CRUD: UPDATE (Async)
@app.put("/api/items/{item_id}", response_model=Item)
async def update_item(item_id: int, updated_item: Item, session: AsyncSession = Depends(get_session)):
    db_item = await session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db_item.title = updated_item.title
    db_item.description = updated_item.description
    db_item.completed = updated_item.completed
    
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return db_item

# CRUD: DELETE (Async)
@app.delete("/api/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, session: AsyncSession = Depends(get_session)):
    item = await session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await session.delete(item)
    await session.commit()
    return None

# Hard-bind the folder path to your absolute Docker WORKDIR location
FRONTEND_DIR = "/workspace/frontend"

# 1. Explicitly serve index.html on direct root (/) requests to prevent 404 loops
@app.get("/")
async def read_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail=f"index.html file missing from static path: {index_path}")

# 2. Mount static asset routing handler to safely resolve CSS/JS assets
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
