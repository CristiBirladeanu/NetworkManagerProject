from sqlmodel import Session, select, create_engine
from models.database import Device
from netmiko import ConnectHandler
import ipaddress

sqlite_file = "database.db"
engine = create_engine(f"sqlite:///{sqlite_file}", echo=False)

def generate_topology_map():
    nodes = {}
    edges = set()

    with Session(engine) as session:
        devices = session.exec(select(Device)).all()

    for dev in devices:
        try:
            conn = ConnectHandler(
                device_type="cisco_ios",
                host=dev.ip_address,
                username=dev.username,
                password=dev.password,
                secret=dev.password
            )
            conn.enable()

            hostname = conn.send_command("show run | include hostname").split()[-1]

            interfaces = {}
            brief_output = conn.send_command("show ip interface brief")
            for line in brief_output.splitlines()[1:]:
                tokens = line.split()
                if len(tokens) >= 6:
                    iface, ip_addr, _, _, line_status, proto_status = tokens[:6]
                    if ip_addr.lower() != "unassigned" and line_status == "up" and proto_status == "up":
                        interfaces[iface] = ip_addr

            ospf_output = conn.send_command("show ip ospf interface brief")
            area_set = set()
            for line in ospf_output.splitlines()[1:]:
                tokens = line.split()
                if len(tokens) >= 3:
                    area_set.add(tokens[2])

            nodes[hostname] = {
                "id": hostname,
                "type": "Router",
                "ip": dev.ip_address,
                "interfaces": interfaces,
                "areas": list(area_set)
            }

            cdp_output = conn.send_command("show cdp neighbors detail")
            current_neighbor = None
            cdp_interfaces = set()

            for line in cdp_output.splitlines():
                if "Device ID:" in line:
                    raw = line.split("Device ID:")[1].strip()
                    current_neighbor = raw.split(".")[0]
                    if current_neighbor not in nodes:
                        nodes[current_neighbor] = {"id": current_neighbor, "type": "Router"}
                elif "Platform:" in line and "Switch" in line:
                    nodes[current_neighbor]["type"] = "Switch"
                elif "Interface:" in line and current_neighbor:
                    parts = line.strip().split(",")
                    local = parts[0].split("Interface:")[1].strip()
                    remote = parts[1].split("Port ID (outgoing port):")[1].strip()
                    if local == "GigabitEthernet0/2" or remote == "GigabitEthernet0/2":
                        continue
                    cdp_interfaces.add(local)
                    edge_key = tuple(sorted([hostname, current_neighbor]))
                    edges.add((edge_key, f"{local} ↔ {remote}"))

            for iface in interfaces:
                if iface in cdp_interfaces or iface == "GigabitEthernet0/2":
                    continue
                output = conn.send_command(f"show ip interface {iface}")
                ip_line = next((l for l in output.splitlines() if "Internet address is" in l), None)
                if not ip_line:
                    continue
                try:
                    if "/" in ip_line:
                        ip_obj = ipaddress.IPv4Interface(ip_line.split("is")[1].strip())
                    else:
                        parts = ip_line.split("Internet address is")[1].split(",")
                        ip_raw = parts[0].strip()
                        mask = parts[1].split("subnet mask is")[1].strip()
                        ip_obj = ipaddress.IPv4Interface(f"{ip_raw}/{mask}")
                except Exception:
                    continue
                if ip_obj.network.prefixlen == 24:
                    net_addr = ip_obj.network.network_address
                    vpcs_id = f"VPCS-{net_addr}/24"
                    if vpcs_id not in nodes:
                        nodes[vpcs_id] = {
                            "id": vpcs_id,
                            "type": "VPCS",
                            "ip": str(net_addr),
                            "note": "Detecție estimativă – host în rețeaua 10.0.x.0/24"
                        }
                    edge_key = tuple(sorted([hostname, vpcs_id]))
                    edges.add((edge_key, f"{iface} ↔ VPCS"))

            conn.disconnect()

        except Exception as e:
            print(f"[Topology] Eroare la {dev.hostname}: {str(e)}")

    return {
        "nodes": list(nodes.values()),
        "edges": [
            {"from": a, "to": b, "label": label} for (a, b), label in edges
        ]
    }

