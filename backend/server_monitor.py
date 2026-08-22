from ssh_service import connect_to_server, run_command
from metrics_parser import parse_cpu, parse_memory, parse_disk


SERVER_IP = "32.198.30.36"
KEY_PATH = r"C:\Users\hP\.ssh\id_ed25519"


def get_server_metrics(server_ip):

    ssh = connect_to_server(
        host=server_ip,
        username="ubuntu",
        key_path=KEY_PATH
    )

    commands = {
        "hostname": "hostname",
        "uptime": "uptime -p",
        "cpu": "top -bn1 | grep 'Cpu(s)'",
        "memory": "free -m",
        "disk": "df -h /",
        "docker": "docker --version"
    }

    raw = {}

    for name, command in commands.items():
        result = run_command(ssh, command)
        raw[name] = result["output"]

    ssh.close()

    cpu_usage = parse_cpu(raw["cpu"])
    memory = parse_memory(raw["memory"])
    disk = parse_disk(raw["disk"])

    return {
        "hostname": raw["hostname"],
        "status": "ONLINE",
        "uptime": raw["uptime"],
        "cpu_usage_percent": cpu_usage,
        "memory": memory,
        "disk": disk,
        "docker": raw["docker"]
    }


if __name__ == "__main__":

    data = get_server_metrics(SERVER_IP)

    print("\n========== SERVER HEALTH ==========")

    print(f"Hostname      : {data['hostname']}")
    print(f"Status        : {data['status']}")
    print(f"Uptime        : {data['uptime']}")
    print(f"CPU Usage     : {data['cpu_usage_percent']}%")

    print("\nRAM:")
    print(f"  Total       : {data['memory']['total_mb']} MB")
    print(f"  Used        : {data['memory']['used_mb']} MB")
    print(f"  Available   : {data['memory']['available_mb']} MB")
    print(f"  Usage       : {data['memory']['usage_percent']}%")

    print("\nDisk:")
    print(f"  Total       : {data['disk']['total']}")
    print(f"  Used        : {data['disk']['used']}")
    print(f"  Available   : {data['disk']['available']}")
    print(f"  Usage       : {data['disk']['usage_percent']}")

    print(f"\nDocker        : {data['docker']}")
