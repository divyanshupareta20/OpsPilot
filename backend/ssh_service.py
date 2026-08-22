import paramiko


def connect_to_server(host, username="ubuntu", key_path=None):

    ssh = paramiko.SSHClient()

    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy()
    )

    ssh.connect(
        hostname=host,
        username=username,
        key_filename=key_path,
        timeout=10
    )

    return ssh


def run_command(ssh, command):

    stdin, stdout, stderr = ssh.exec_command(
        command
    )

    output = stdout.read().decode().strip()

    error = stderr.read().decode().strip()

    exit_code = stdout.channel.recv_exit_status()

    return {
        "output": output,
        "error": error,
        "exit_code": exit_code
    }