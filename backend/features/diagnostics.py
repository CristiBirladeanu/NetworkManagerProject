from fastapi import APIRouter
from models.api_schemas import PingRequest, InterfaceRequest, OSPFStatusRequest, InterfaceSelectRequest, InterfaceConfigRequest, InterfaceConfigResponse
from services.diagnostics_service import run_ping_command, run_interface_command, get_ospf_status, list_active_interfaces, get_interface_config
from services.logs_service import save_command_log

router = APIRouter()


@router.post("/ping")
def ping(request: PingRequest):
    output = run_ping_command(
        request.ip, request.username, request.password, request.destination
    )
    save_command_log(
        ip=request.ip,
        username=request.username,
        command=f"ping {request.destination}",
        output=output
    )
    return {"output": output}


@router.post("/interfaces")
def interfaces(request: InterfaceRequest):
    output = run_interface_command(
        request.ip, request.username, request.password
    )
    save_command_log(
        ip=request.ip,
        username=request.username,
        command="show ip interface brief",
        output=output
    )
    return {"output": output}


@router.post("/ospf_status")
def ospf_status(request: OSPFStatusRequest):
    result = get_ospf_status(
        request.ip, request.username, request.password
    )
    if "error" in result:
        save_command_log(
            ip=request.ip,
            username=request.username,
            command="show ip ospf neighbor + show ip route ospf",
            output=result["error"]
        )
    else:
        combined_output = result["neighbors"] + "\n" + result["routes"]
        save_command_log(
            ip=request.ip,
            username=request.username,
            command="show ip ospf neighbor + show ip route ospf",
            output=combined_output
        )

    return result

@router.post("/interfaces_list")
def interfaces_list(request: InterfaceSelectRequest):
    return list_active_interfaces(
        ip=request.ip,
        username=request.username,
        password=request.password
    )


@router.post("/interface_config", response_model=InterfaceConfigResponse)
def interface_config(request: InterfaceConfigRequest):
    return get_interface_config(
        ip=request.ip,
        username=request.username,
        password=request.password,
        interface=request.interface
    )


