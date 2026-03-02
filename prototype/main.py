from fastapi import FastAPI

from router.workout_router import router as workout_router

app = FastAPI(title="Workout Tracker Event API")
app.include_router(workout_router)

#mqin route
@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Workout tracker event API is running."}