from typing import List, Optional
from fastapi import FastAPI, Response, HTTPException, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="FastAPI Security & CRUD Lab")

# 1. Keep your working CSP Header Middleware intact
@app.middleware("http")
async def add_security_headers(request, call_next):
    response: Response = await call_next(request)
    response.headers["Content-Security-Policy"] = "script-src 'self';"
    return response

# 2. Define the Pydantic schema for your data validation
class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float

# 3. Simulated database list
db_items: List[Item] = [
    Item(id=1, name="Sample Item", description="An initial testing asset", price=19.99)
]

# ─── CRUD ENDPOINTS ─────────────────────────────────────────────────────────

# CREATE: Add a new item
@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(item: Item):
    # Check if ID already exists
    if any(x.id == item.id for x in db_items):
        raise HTTPException(status_code=400, detail="Item with this ID already exists.")
    db_items.append(item)
    return item

# READ ALL: Get all items
@app.get("/items", response_model=List[Item])
def get_all_items():
    return db_items

# READ ONE: Get a single item by ID
@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    for item in db_items:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found.")

# UPDATE: Modify an existing item
@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, updated_item: Item):
    for index, item in enumerate(db_items):
        if item.id == item_id:
            db_items[index] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found.")

# DELETE: Remove an item
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    for index, item in enumerate(db_items):
        if item.id == item_id:
            db_items.pop(index)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail="Item not found.")

# 4. Mount your frontend directory to serve UI pages
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
