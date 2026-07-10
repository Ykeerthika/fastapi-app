from typing import List, Optional
from fastapi import FastAPI, Response, HTTPException, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Initialize the application
app = FastAPI(title="FastAPI Security & CRUD Lab")

# 1. CONTENT SECURITY POLICY MIDDLEWARE
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    
    # Skip CSP blocking for the documentation pages so they can render
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
        return response
        
    # Enforce strict safety on your regular application endpoints and front-end
    response.headers["Content-Security-Policy"] = "script-src 'self';"
    return response

# 2. DATA VALIDATION SCHEMA
class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float

# 3. MOCK DATA BASE STORAGE
db_items: List[Item] = [
    Item(id=1, name="Production Server", description="Hosted via Coolify", price=45.00)
]

# 4. API CRUD ENDPOINTS
# (Must be written above the static mount to show up in your /docs panel)

@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(item: Item):
    """Creates a new item inside the system."""
    if any(x.id == item.id for x in db_items):
        raise HTTPException(status_code=400, detail="Item with this ID already exists.")
    db_items.append(item)
    return item

@app.get("/items", response_model=List[Item])
def get_all_items():
    """Retrieves all tracked database items."""
    return db_items

@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    """Fetches a specific item using its unique ID."""
    for item in db_items:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found.")

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, updated_item: Item):
    """Overwrites an existing item configuration."""
    for index, item in enumerate(db_items):
        if item.id == item_id:
            db_items[index] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found.")

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    """Permanently purges an entry from the system repository."""
    for index, item in enumerate(db_items):
        if item.id == item_id:
            db_items.pop(index)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail="Item not found.")

# 5. FRONTEND STATIC FILE DIRECTORY MOUNT
# (Keep this line as the literal bottom statement of your code file)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
