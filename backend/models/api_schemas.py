from pydantic import BaseModel
from typing import List, Optional

class ConnectionCredentials(BaseModel):
    ip: str
    username: str
    password: str

class SSHRequest(ConnectionCredentials):
    command: str

class PingRequest(ConnectionCredentials):
    destination: str

class InterfaceRequest(ConnectionCredentials):
    pass

class NetworkConfig(BaseModel):
    ip: str
    wildcard: str
    area: int

class OSPFRequest(ConnectionCredentials):
    process_id: int
    networks: List[NetworkConfig]

class OSPFStatusRequest(ConnectionCredentials):
    pass

class OSPFResetRequest(ConnectionCredentials):
    process_id: int
    mode: str  

class OSPFAutoDiscoverRequest(ConnectionCredentials):
    mgmt_network: Optional[str] = None  

class InterfaceSelectRequest(ConnectionCredentials):
    pass

class InterfaceConfigRequest(ConnectionCredentials):
    interface: str

class InterfaceConfigResponse(BaseModel):
    interface: str
    ip: Optional[str]
    status: Optional[str]
    info: str 
    config: str 

class ProxyRequest(BaseModel):
    via_ip: str
    via_username: str
    via_password: str
    target_ip: str
    target_commands: List[str]


