from fastapi import FastAPI

app = FastAPI(
    title="Web Frameworks Tutorial API",
    description="API for the Web Frameworks Tutorial Platform",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Web Frameworks Tutorial API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}