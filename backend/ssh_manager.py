import paramiko


def run_ssh_command(host, username, password, command):
    ssh = paramiko.SSHClient()

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(
        hostname=host,
        username=username,
        password=password,
        timeout=10
    )

    stdin, stdout, stderr = ssh.exec_command(command)

    output = stdout.read().decode().strip()

    ssh.close()

    return output