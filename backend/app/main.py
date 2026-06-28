from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {
        "project": "AI Lawyer Assistant",
        "status": "Running Successfully",
        "version": "1.0.0"
    }