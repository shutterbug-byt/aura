from fastapi import FastAPI

app = FastAPI(title = "AURA")


@app.get("/")
def home():
    return {"message": "AURA backend is running!"}