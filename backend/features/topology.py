from fastapi import APIRouter
from services.topology_service import generate_topology_map

router = APIRouter()

@router.get("/topology_map")
def get_topology_map():
    return generate_topology_map()

