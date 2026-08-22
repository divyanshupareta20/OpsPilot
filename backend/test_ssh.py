from ssh_service import connect_to_server, run_command


SERVER_IP = "3.237.69.171"
KEY_PATH = r"C:\Users\hP\.ssh\id_ed25519"


ssh = connect_to_server(
    host=SERVER_IP,
    username="ubuntu",
    key_path=KEY_PATH
)

result = run_command(ssh, "hostname && uptime")

print("SERVER OUTPUT:")
print(result["output"])

if result["error"]:
    print("ERROR:")
    print(result["error"])

ssh.close()