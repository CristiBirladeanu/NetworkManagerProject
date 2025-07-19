from netmiko import ConnectHandler
from typing import List, Dict, Set
from models.database import get_session, Device
from sqlmodel import select
from services.proxy_service import execute_proxy_command
import re

def discover_devices(seed_ip: str, username: str, password: str) -> List[Dict]:
    discovered_devices = []
    visited_ips: Set[str] = set()
    map_ip_to_hostname: Dict[str, str] = {}

    def try_ssh(ip: str) -> tuple:
        print(f"[STEP] SSH direct → {ip}")
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
            hostname_output = conn.send_command("show run | include hostname")
            hostname_match = re.search(r"hostname\s+(\S+)", hostname_output)
            hostname = hostname_match.group(1) if hostname_match else ip
            print(f"[OK] Conectat direct → hostname={hostname}")

            cdp_output = conn.send_command("show cdp neighbors detail")
            conn.disconnect()
            return hostname, cdp_output
        except Exception as e:
            print(f"[ERROR] SSH direct eșuat pentru {ip}: {str(e)}")
            return None, None

    def try_proxy(via_ip: str, target_ip: str) -> tuple:
        print(f"[STEP] Proxy SSH → via={via_ip} → target={target_ip}")
        try:
            result = execute_proxy_command(
                via_ip=via_ip,
                via_username=username,
                via_password=password,
                target_ip=target_ip,
                target_commands=[
                    "show run | include hostname",
                    "show cdp neighbors detail"
                ]
            )
            steps = result.get("steps", [])
            for line in steps:
                print(f"[PROXY] {line}")

            hostname = "UNKNOWN"
            for step in steps:
                if "hostname" in step.lower():
                    parts = step.split("→")
                    if len(parts) > 1:
                        hostname_line = parts[1].strip()
                        hostname = hostname_line.split()[1] if "hostname" in hostname_line else hostname_line.split()[0]
                        break

            print(f"[OK] Proxy SSH → hostname={hostname}")

            cdp_output = "\n".join([s for s in steps if "IP address" in s or "Device ID" in s])
            return hostname, cdp_output
        except Exception as e:
            print(f"[ERROR] Proxy SSH eșuat pentru {target_ip}: {str(e)}")
            return None, None

    def connect_and_extract(ip: str, parent_ip: str = None):
        if ip in visited_ips:
            print(f"[SKIP] {ip} deja procesat")
            return
        visited_ips.add(ip)

        print(f"[INFO] Procesare IP: {ip}")
        hostname, cdp_output = try_ssh(ip)

        if not hostname:
            print(f"[WARN] SSH direct eșuat pentru {ip}, încerc proxy prin {parent_ip}")
            hostname, cdp_output = try_proxy(parent_ip, ip)

        if not hostname or hostname == "UNKNOWN":
            # Fallback la CDP dacă avem IP în map
            if ip in map_ip_to_hostname:
                hostname = map_ip_to_hostname[ip]
                print(f"[FALLBACK] Nume dedus din CDP pentru {ip}: {hostname}")

        if not hostname:
            print(f"[FAIL] Nu s-a putut obține hostname pentru {ip}")
            hostname = "UNKNOWN"

        # Înregistrăm doar dacă nu există deja
        existing = next((d for d in discovered_devices if d["ip_address"] == ip), None)
        if not existing:
            discovered_devices.append({
                "hostname": hostname,
                "ip_address": ip,
                "username": username,
                "password": password
            })
            print(f"[ADD] {hostname} ({ip}) adăugat la lista de device-uri")

        if not cdp_output:
            print(f"[WARN] Nu s-au extras vecini CDP pentru {ip}")
            return

        print(f"[CDP] Încep parsarea vecinilor pentru {ip}")
        blocks = cdp_output.split("-------------------------")
        for block in blocks:
            ip_match = re.search(r"IP address: (\d+\.\d+\.\d+\.\d+)", block)
            id_match = re.search(r"Device ID: (\S+)", block)

            if ip_match and id_match:
                neighbor_ip = ip_match.group(1)
                neighbor_id = id_match.group(1).split(".")[0]
                map_ip_to_hostname[neighbor_ip] = neighbor_id  # 🔥 asociem IP ↔ hostname
                print(f"[CDP] Vecin detectat: {neighbor_ip} (hostname: {neighbor_id})")
                connect_and_extract(neighbor_ip, parent_ip=ip)
            elif ip_match:
                neighbor_ip = ip_match.group(1)
                print(f"[CDP] Vecin detectat: {neighbor_ip}")
                connect_and_extract(neighbor_ip, parent_ip=ip)
            elif id_match:
                print(f"[CDP] Vecin fără IP: {id_match.group(1)} — ignorat")

    connect_and_extract(seed_ip)

    with get_session() as session:
        for dev in discovered_devices:
            exists = session.exec(select(Device).where(Device.ip_address == dev["ip_address"])).first()
            if not exists:
                session.add(Device(
                    hostname=dev["hostname"],
                    ip_address=dev["ip_address"],
                    username=username,
                    password=password
                ))
                print(f"[DB] Salvat în DB: {dev['hostname']} ({dev['ip_address']})")
        session.commit()

    return discovered_devices
