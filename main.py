import fastapi
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from Elevator import Elevator


# request pydantic models
class FloorRequest(BaseModel):
    floor: int
    direction: int  # -1 for down, 0 for internal, 1 for up

class StepRequest(BaseModel):
    steps: int = 1 # default to 1 step

class ResetRequest(BaseModel):
    pass  # No parameters needed for reset


app = FastAPI(title="Elevator API")
elevator = Elevator("car-1", maxFloor=10, timePerFloor=2.0)

@app.get("/")
def getStatus():
    return {"service": "elevator", "status": "ready"}


@app.get("/api/elevator")
def getState():
    return elevator.status()


@app.post("/api/elevator/request")
def requestFloor(request: FloorRequest):
    try:
        elevator.requestFloor(request.floor, request.direction)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return getState()

@app.post("/api/elevator/step")
def stepElevator(request: StepRequest):
    try:
        elevator.step(request.steps)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return getState()


@app.post("/api/elevator/reset")
def resetElevator():
    """Reset elevator to default state (floor 0, idle)"""
    try:
        return elevator.reset()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

