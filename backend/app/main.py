from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.database import (
    create_scan_record,
    create_target,
    delete_target,
    get_scan_record,
    get_scan_report_by_id,
    get_target,
    init_db,
    list_scan_records,
    list_targets,
    update_target_authorization,
)
from backend.app.models import NmapBasicScanRequest, TargetAuthorizationUpdate, TargetCreate
from backend.app.modules.nmap_scan import run_basic_nmap_scan_for_target, write_report
from backend.app.modules.target_validation import validate_target_input


FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend" / "simple_ui"

app = FastAPI(
    title="Cyber Lab Control Panel",
    description="Local defensive cybersecurity testing dashboard for authorized assets only.",
    version="0.5.0",
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


@app.get("/ui", include_in_schema=False)
def serve_ui_index():
    return FileResponse(FRONTEND_DIR / "index.html")


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


@app.post("/scans/nmap/basic")
def run_nmap_basic_scan_endpoint(payload: NmapBasicScanRequest):
    target = get_target(payload.target_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Target not found.")

    if not target["authorized"]:
        raise HTTPException(status_code=403, detail="Target is not authorized for scanning.")

    validation = validate_target_input(target["target"])
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["error"])

    scan_result = run_basic_nmap_scan_for_target(target)
    if not scan_result["success"] and not scan_result["command_used"]:
        raise HTTPException(status_code=400, detail=scan_result["stderr"])

    scan_record = create_scan_record(
        target_id=scan_result.get("target_id"),
        target=scan_result.get("target") or target["target"],
        target_type=scan_result.get("target_type"),
        scan_type=scan_result.get("scan_type") or "nmap_basic",
        status="completed" if scan_result.get("success") else "failed",
        success=bool(scan_result.get("success")),
        report_file=scan_result.get("report_file"),
        summary=scan_result.get("summary"),
        started_at=scan_result.get("started_at"),
        finished_at=scan_result.get("finished_at"),
    )
    scan_result["scan_id"] = scan_record["id"]
    scan_result["status"] = scan_record["status"]
    if scan_result.get("report_file"):
        write_report(scan_result)

    return scan_result


@app.get("/scans")
def list_scans_endpoint(limit: int = Query(default=50, ge=1, le=200)):
    return {"success": True, "scans": list_scan_records(limit)}


@app.get("/scans/{scan_id}")
def get_scan_endpoint(scan_id: int):
    scan = get_scan_record(scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return {"success": True, "scan": scan}


@app.get("/scans/{scan_id}/report")
def get_scan_report_endpoint(scan_id: int):
    report = get_scan_report_by_id(scan_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Scan report not found.")
    return {"success": True, "scan_id": scan_id, "report": report}

app.mount("/ui", StaticFiles(directory=FRONTEND_DIR), name="simple_ui")

