from fastapi import FastAPI
from features import diagnostics, configurations, logs, devices, topology, proxy
from fastapi.middleware.cors import CORSMiddleware
from models.database import create_db_and_tables, reset_database

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Creează tabele (dacă nu există deja)
create_db_and_tables()

@app.on_event("startup")
def startup():
    reset_database()

# Include routerele
app.include_router(configurations.router)
app.include_router(diagnostics.router)
app.include_router(logs.router)
app.include_router(devices.router)
app.include_router(topology.router)
app.include_router(proxy.router)

@app.get("/")
def read_root():
    return {"status": "FastAPI backend is running"}

