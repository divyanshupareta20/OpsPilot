from ssh_service import connect_to_server, run_command

SERVER_IP = "32.198.30.36"
KEY_PATH = r"C:\Users\hP\.ssh\id_ed25519"


def get_docker_info(server_ip):

    ssh = connect_to_server(
        host=server_ip,
        username="ubuntu",
        key_path=KEY_PATH
    )

    commands = {
        "version": "docker --version",
        "containers": "docker ps -a --format '{{json .}}'",
        "images": "docker images --format '{{json .}}'"
    }

    result = {}

    for name, command in commands.items():

        data = run_command(ssh, command)

        result[name] = {
            "output": data["output"],
            "error": data["error"],
            "exit_code": data["exit_code"]
        }

    ssh.close()

    return result


if __name__ == "__main__":

    data = get_docker_info(SERVER_IP)

    print("\n========== DOCKER MONITOR ==========")

    print("\nDocker Version:")
    print(data["version"]["output"])

    print("\nContainers:")
    print(data["containers"]["output"])

    print("\nImages:")
    print(data["images"]["output"])