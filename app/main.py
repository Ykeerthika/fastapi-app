from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Middleware to apply the strict CSP rule you encountered
@app.middleware("http")
async def add_security_headers(request, call_next):
    response: Response = await call_next(request)
    # This header blocks unsafe evaluation ('unsafe-eval') across the app
    response.headers["Content-Security-Policy"] = "script-src 'self';"
    return response

# Serve your static frontend files (assuming your repository structure)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
