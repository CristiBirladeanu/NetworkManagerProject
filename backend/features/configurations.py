from fastapi import APIRouter
from models.api_schemas import SSHRequest, OSPFRequest, OSPFResetRequest, OSPFAutoDiscoverRequest
from services.config_service import run_command, configure_ospf, reset_ospf, discover_ospf_networks
from services.logs_service import save_command_log

router = APIRouter()


@router.post("/connect")
def connect(request: SSHRequest):
    output = run_command(
        request.ip, request.username, request.password, request.command
    )
    save_command_log(
        ip=request.ip,
        username=request.username,
        command=request.command,
        output=output
    )
    return {"output": output}


@router.post("/ospf_configure")
def ospf_configure(request: OSPFRequest):
    output = configure_ospf(
        request.ip, request.username, request.password,
        request.process_id, request.networks
    )
    ospf_commands_summary = f"router ospf {request.process_id} with {len(request.networks)} networks"
    save_command_log(
        ip=request.ip,
        username=request.username,
        command=ospf_commands_summary,
        output=output
    )
    return {"output": output}

@router.post("/ospf_reset")
def ospf_reset(request: OSPFResetRequest):
    return {
        "output": reset_ospf(
            ip=request.ip,
            username=request.username,
            password=request.password,
            process_id=request.process_id,
            mode=request.mode
        )
    }

@router.post("/ospf_autodiscover")
def ospf_autodiscover(request: OSPFAutoDiscoverRequest):
    return discover_ospf_networks(
        ip=request.ip,
        username=request.username,
        password=request.password,
        mgmt_network=request.mgmt_network
    )

