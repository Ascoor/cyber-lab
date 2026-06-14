from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.app.database import (
    create_target,
    delete_target,
    get_target,
    init_db,
    list_targets,
    update_target_authorization,
)
from backend.app.models import TargetAuthorizationUpdate, TargetCreate
from backend.app.modules.target_validation import validate_target_input

app = FastAPI(
    title="Cyber Lab Control Panel",
    description="Local defensive cybersecurity testing dashboard for authorized assets only.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
def home():
    return {
        "status": "running",
        "message": "Cyber Lab Control Panel is ready",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
    }


@app.post("/targets")
def create_target_endpoint(payload: TargetCreate):
    validation = validate_target_input(payload.target)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["error"])

    detected_target_type = validation["target_type"]
    if payload.target_type is not None and payload.target_type != detected_target_type:
        raise HTTPException(
            status_code=400,
            detail=f"Provided target_type must match detected target_type: {detected_target_type}.",
        )

    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Target name must not be empty.")

    target = create_target(
        name=name,
        target=validation["normalized_target"],
        target_type=detected_target_type,
        authorized=payload.authorized,
        scope_notes=payload.scope_notes,
    )
    return {"success": True, "target": target}


@app.get("/targets")
def list_targets_endpoint():
    return {"success": True, "targets": list_targets()}


@app.get("/targets/{target_id}")
def get_target_endpoint(target_id: int):
    target = get_target(target_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Target not found.")
    return {"success": True, "target": target}


@app.patch("/targets/{target_id}/authorization")
def update_target_authorization_endpoint(target_id: int, payload: TargetAuthorizationUpdate):
    target = update_target_authorization(target_id, payload.authorized)
    if target is None:
        raise HTTPException(status_code=404, detail="Target not found.")
    return {"success": True, "target": target}


@app.delete("/targets/{target_id}")
def delete_target_endpoint(target_id: int):
    deleted = delete_target(target_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Target not found.")
    return {"success": True}
