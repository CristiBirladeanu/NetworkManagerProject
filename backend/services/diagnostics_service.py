from netmiko import ConnectHandler

def run_ping_command(ip: str, username: str, password: str, destination: str) -> str:
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
        output = conn.send_command(f"ping {destination}")
        conn.disconnect()
        return output
    except Exception as e:
        return f"Error: {str(e)}"

def run_interface_command(ip: str, username: str, password: str) -> str:
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
        output = conn.send_command("show ip interface brief")
        conn.disconnect()
        return output
    except Exception as e:
        return f"Error: {str(e)}"

def get_ospf_status(ip: str, username: str, password: str) -> dict:
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
        
        neighbors = conn.send_command("show ip ospf neighbor")
        routes = conn.send_command("show ip route ospf")
        conn.disconnect()
        return {"neighbors": neighbors, "routes": routes}
    except Exception as e:
        return {"error": str(e)}

def list_active_interfaces(ip: str, username: str, password: str) -> list[str]:
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

        output = conn.send_command("show ip interface brief")
        interfaces = []

        for line in output.splitlines()[1:]:
            tokens = line.split()
            if len(tokens) >= 6:
                iface, ip_addr, _, _, line_status, proto_status = tokens[:6]
                if ip_addr.lower() != "unassigned" and line_status == "up" and proto_status == "up":
                    interfaces.append(iface)

        conn.disconnect()
        return interfaces
    except Exception as e:
        return [f"Error: {str(e)}"]


def get_interface_config(ip: str, username: str, password: str, interface: str) -> dict:
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

        info = conn.send_command(f"show ip interface {interface}")
        config = conn.send_command(f"show run interface {interface}")

        ip_line = next((l for l in info.splitlines() if "Internet address is" in l), None)
        ip = None
        if ip_line:
            ip = ip_line.split("is")[1].strip().split()[0]

        status_line = next((l for l in info.splitlines() if "line protocol" in l), None)
        status = None
        if status_line:
            status = status_line.strip()

        conn.disconnect()

        return {
            "interface": interface,
            "ip": ip,
            "status": status,
            "info": info,
            "config": config
        }

    except Exception as e:
        return {
            "interface": interface,
            "ip": None,
            "status": None,
            "info": f"Error: {str(e)}",
            "config": ""
        }

