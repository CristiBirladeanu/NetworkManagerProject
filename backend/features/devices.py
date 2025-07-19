# features/devices.py

from fastapi import APIRouter, Query
from typing import List
from services.device_discovery_service import discover_devices

router = APIRouter()

@router.get("/devices")
def discover_devices_live(
    seed_ip: str = Query(..., description="IP al routerului de pornire"),
    username: str = Query(...),
    password: str = Query(...)
) -> List[dict]:
    """
    Descoperă rețeaua în mod recursiv folosind SSH direct și fallback pe proxy.
    Returnează hostname, IP și pașii de debug per nod.
    """
    return discover_devices(seed_ip, username, password)
