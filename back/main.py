from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Raccoons rule"}

@app.get("/raccoons")
async def root():
    return "THIS IS THE RACCOON PAGE"


