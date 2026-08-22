def parse_cpu(cpu_output):
    parts = cpu_output.split(",")

    idle = 0.0

    for part in parts:
        if "id" in part:
            idle = float(part.strip().split()[0])

    return round(100 - idle, 2)


def parse_memory(memory_output):
    lines = memory_output.splitlines()

    values = lines[1].split()

    total = int(values[1])
    used = int(values[2])
    available = int(values[6])

    usage_percent = round((used / total) * 100, 2)

    return {
        "total_mb": total,
        "used_mb": used,
        "available_mb": available,
        "usage_percent": usage_percent
    }


def parse_disk(disk_output):
    lines = disk_output.splitlines()

    values = lines[1].split()

    return {
        "total": values[1],
        "used": values[2],
        "available": values[3],
        "usage_percent": values[4]
    }