from fastapi import FastAPI

app = FastAPI()


# import routes here
#create a controller, a datamapper, and then map all 
# routes in a routerm then call therouters here, then 
# crate middlewares like jwt etc - and protect routes in router for example. just like we learned to do an old API

@app.get("/")
async def root():
    return {"message": "Raccoons rule"}

@app.get("/raccoons")
async def root():
    return "THIS IS THE RACCOON PAGE"

@app.get("/users")
async def root():
    return "RACCONS RULE"

@app.get("/testingnoise")
async def root():
    return "JUST TESTING THE NOISE"

@app.get("/home")
async def root():
    return {"key": "value"}
