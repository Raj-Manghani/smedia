from fastapi import FastAPI

app = FastAPI(title="Smedia Backend API")

@app.get("/")
async def root():
    return {"message": "Welcome to the Smedia Backend API"}

@app.get("/health")
async def health():
    return {"status": "ok"}
