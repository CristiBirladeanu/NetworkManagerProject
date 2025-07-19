# features/proxy.py

from fastapi import APIRouter
from models.api_schemas import ProxyRequest
from services.proxy_service import execute_proxy_command

router = APIRouter()

@router.post("/proxy_connect")
def proxy_connect(request: ProxyRequest):
    """
    Execută comenzi pe un dispozitiv nerutabil folosind SSH nested printr-un router seed.
    """
    result = execute_proxy_command(
        via_ip=request.via_ip,
        via_username=request.via_username,
        via_password=request.via_password,
        target_ip=request.target_ip,
        target_commands=request.target_commands
    )
    return result
