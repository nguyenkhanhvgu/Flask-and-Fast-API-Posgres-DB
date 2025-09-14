from fastapi import FastAPI
from .routers import auth, content, progress, exercises, search

app = FastAPI(
    title="Web Frameworks Tutorial API",
    description="API for the Web Frameworks Tutorial Platform",
    version="1.0.0"
)

# Include routers
app.include_router(auth.router)
app.include_router(content.router)
app.include_router(progress.router)
app.include_router(exercises.router)
app.include_router(search.router)

@app.get("/")
async def root():
    return {"message": "Web Frameworks Tutorial API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}