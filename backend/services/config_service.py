from netmiko import ConnectHandler
from models.api_schemas import NetworkConfig
from typing import Optional
import time 
import ipaddress


def run_command(ip: str, username: str, password: str, command: str) -> str:
    try:
        device = {
            "device_type": "cisco_ios",
            "host": ip,
            "username": username,
            "password": password,
            "secret": password
        }
        conn = ConnectHandler(**device)
        conn.enable()
        output = conn.send_command(command)
        conn.disconnect()
        return output
    except Exception as e:
        return f"Error: {str(e)}"

def configure_ospf(ip: str, username: str, password: str, process_id: int, networks: list[NetworkConfig]) -> str:
    try:
        device = {
            "device_type": "cisco_ios",
            "host": ip,
            "username": username,
            "password": password,
            "secret": password
        }
        conn = ConnectHandler(**device)
        conn.enable()

        commands = [f"router ospf {process_id}"]
        for net in networks:
            commands.append(f"network {net.ip} {net.wildcard} area {net.area}")

        output = conn.send_config_set(commands)
        output += "\n" + conn.save_config()

        conn.disconnect()
        return output
    except Exception as e:
        return f"Error: {str(e)}"

def reset_ospf(ip: str, username: str, password: str, process_id: int, mode: str) -> str:
    try:
        device = {
            "device_type": "cisco_ios",
            "host": ip,
            "username": username,
            "password": password,
            "secret": password
        }
        conn = ConnectHandler(**device)
        conn.enable()

        if mode == "restart":
            conn.write_channel("clear ip ospf process\n")
            time.sleep(1)
            output = conn.read_channel()

            if "Reset ALL OSPF processes" in output:
                conn.write_channel("yes\n")
                time.sleep(2)
                output += conn.read_channel()
        elif mode == "remove":
            output = conn.send_config_set([f"no router ospf {process_id}"])
            output += "\n" + conn.save_config()
        else:
            return f"Error: Mod de reset invalid: {mode}"

        conn.disconnect()
        return output
    except Exception as e:
        return f"Error: {str(e)}"

def discover_ospf_networks(ip: str, username: str, password: str, mgmt_network: Optional[str] = None) -> list[NetworkConfig]:
    try:
        device = {
            "device_type": "cisco_ios",
            "host": ip,
            "username": username,
            "password": password,
            "secret": password
        }

        conn = ConnectHandler(**device)
        conn.enable()

        interfaces = set()
        cdp_output = conn.send_command("show cdp neighbors detail")
        for line in cdp_output.splitlines():
            if "Interface:" in line:
                parts = line.strip().split(",")
                for part in parts:
                    if "Interface:" in part:
                        iface = part.split("Interface:")[1].strip()
                        interfaces.add(iface)

        brief_output = conn.send_command("show ip interface brief")
        for line in brief_output.splitlines()[1:]:
            tokens = line.split()
            if len(tokens) >= 6:
                iface, ip_addr, _, _, line_status, proto_status = tokens[:6]
                if ip_addr.lower() != "unassigned" and line_status == "up" and proto_status == "up":
                    interfaces.add(iface)

        exclude_net = None
        if mgmt_network:
            try:
                exclude_net = ipaddress.IPv4Network(mgmt_network)
            except ValueError:
                pass

        discovered = set()
        networks = []

        for iface in interfaces:
            output = conn.send_command(f"show ip interface {iface}")
            ip_line = next((l for l in output.splitlines() if "Internet address is" in l), None)
            if not ip_line:
                continue

            try:
                if "/" in ip_line:
                    ip_info = ip_line.split("Internet address is")[1].strip()
                    ip_obj = ipaddress.IPv4Interface(ip_info)
                else:
                    parts = ip_line.split("Internet address is")[1].strip().split(",")
                    ip_addr = parts[0].strip()
                    mask_part = next((p for p in parts if "subnet mask is" in p), None)
                    if not mask_part:
                        continue
                    mask_str = mask_part.split("subnet mask is")[1].strip()
                    ip_obj = ipaddress.IPv4Interface(f"{ip_addr}/{mask_str}")
            except Exception:
                continue

            if exclude_net and ip_obj.ip in exclude_net:
                continue

            network_ip = str(ip_obj.network.network_address)
            wildcard = str(ip_obj.network.hostmask)
            key = (network_ip, wildcard)

            if key not in discovered:
                discovered.add(key)
                networks.append(NetworkConfig(ip=network_ip, wildcard=wildcard, area=0))

        conn.disconnect()
        return networks

    except Exception as e:
        return [NetworkConfig(ip="error", wildcard=str(e), area=0)]

