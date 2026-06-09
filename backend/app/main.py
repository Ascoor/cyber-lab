from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Cyber Lab Control Panel",
    description="Local defensive cybersecurity testing dashboard for authorized assets only.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "status": "running",
        "message": "Cyber Lab Control Panel is ready"
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }
