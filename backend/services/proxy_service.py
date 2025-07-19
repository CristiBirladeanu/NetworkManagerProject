# services/proxy_service.py

from netmiko import ConnectHandler
from typing import List, Dict


def execute_proxy_command(
    via_ip: str,
    via_username: str,
    via_password: str,
    target_ip: str,
    target_commands: List[str]
) -> Dict[str, str]:
    output_log = {
        "via_device": via_ip,
        "target_device": target_ip,
        "steps": []
    }

    try:
        conn = ConnectHandler(
            device_type="cisco_ios",
            host=via_ip,
            username=via_username,
            password=via_password,
            secret=via_password,
        )
        conn.enable()
        output_log["steps"].append(f"[CONNECTED] Seed {via_ip}")

        # ✅ SSH valid pentru IOS:
        ssh_command = f"ssh -l {via_username} {target_ip}"
        output = conn.send_command_timing(ssh_command)
        if "assword" in output or "Password" in output:
            output = conn.send_command_timing(via_password)
            output_log["steps"].append(f"[NESTED SSH] Connected to {target_ip}")
        else:
            output_log["steps"].append(f"[ERROR] SSH prompt not found: {output}")
            conn.disconnect()
            return output_log

        for cmd in target_commands:
            cmd_output = conn.send_command_timing(cmd)
            output_log["steps"].append(f"[CMD] {cmd} → {cmd_output.strip()}")

        conn.send_command_timing("exit")
        output_log["steps"].append(f"[EXIT TARGET] Sesie închisă către {target_ip}")

        conn.disconnect()
        output_log["steps"].append("[DONE] Conexiune închisă complet.")

    except Exception as e:
        output_log["steps"].append(f"[ERROR] {str(e)}")

    return output_log
