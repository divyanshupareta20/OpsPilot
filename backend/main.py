import asyncio
import threading
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import modules
from database import engine, SessionLocal, Base
from server_monitor import get_server_metrics
from ssh_service import connect_to_server, run_command


# =========================================================
# DATABASE
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# AUTOMATIC SERVER MONITORING
# =========================================================

async def automatic_monitor():

    while True:

        db = SessionLocal()

        try:

            servers = db.query(modules.Server).all()

            for server in servers:

                try:

                    data = await asyncio.to_thread(
                        get_server_metrics,
                        server.ip_address
                    )

                    server.status = "online"
                    server.health_status = "healthy"

                    server.cpu_usage = data[
                        "cpu_usage_percent"
                    ]

                    server.ram_usage = data[
                        "memory"
                    ]["usage_percent"]

                    server.disk_usage = float(
                        data["disk"]["usage_percent"]
                        .replace("%", "")
                    )

                    server.hostname = data["hostname"]
                    server.uptime = data["uptime"]

                    server.last_checked = datetime.utcnow()

                    print(
                        f"[MONITOR] {server.name} | "
                        f"CPU: {server.cpu_usage}% | "
                        f"RAM: {server.ram_usage}% | "
                        f"Disk: {server.disk_usage}%"
                    )

                except Exception as e:

                    server.status = "offline"
                    server.health_status = "unhealthy"

                    server.last_checked = datetime.utcnow()

                    print(
                        f"[MONITOR ERROR] "
                        f"{server.name}: {str(e)}"
                    )

            db.commit()

        except Exception as e:

            print(
                f"[MONITOR SYSTEM ERROR] {str(e)}"
            )

        finally:

            db.close()

        await asyncio.sleep(60)


# =========================================================
# LIFESPAN
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    monitoring_task = asyncio.create_task(
        automatic_monitor()
    )

    print("====================================")
    print(" OpsPilot Automatic Monitoring Started")
    print(" Monitoring interval: 60 seconds")
    print("====================================")

    yield

    monitoring_task.cancel()

    try:

        await monitoring_task

    except asyncio.CancelledError:

        pass


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="OpsPilot API",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# DATABASE SESSION
# =========================================================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "message": "OpsPilot Backend is running"
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# =========================================================
# ADD SERVER
# =========================================================

@app.post("/servers")
def add_server(
    name: str,
    ip_address: str,
    status: str = "unknown",
    db: Session = Depends(get_db)
):

    server = modules.Server(

        name=name,

        ip_address=ip_address,

        status=status

    )

    db.add(server)

    db.commit()

    db.refresh(server)

    return server


# =========================================================
# GET SERVERS
# =========================================================

@app.get("/servers")
def get_servers(
    db: Session = Depends(get_db)
):

    return db.query(
        modules.Server
    ).all()

# =========================================================
# UPDATE SERVER
# =========================================================

@app.put("/servers/{server_id}")
def update_server(
    server_id: int,
    name: str,
    ip_address: str,
    status: str,
    db: Session = Depends(get_db)
):

    server = db.query(
        modules.Server
    ).filter(
        modules.Server.id == server_id
    ).first()

    if not server:

        return {
            "error": "Server not found"
        }

    server.name = name
    server.ip_address = ip_address
    server.status = status

    db.commit()

    db.refresh(server)

    activity = modules.Activity(
        action="Server Updated",
        description=f"Server {server.name} was updated",
        entity_type="server",
        entity_id=server.id,
        status="success"
    )

    db.add(activity)

    db.commit()

    return server


# =========================================================
# DELETE SERVER
# =========================================================

@app.delete("/servers/{server_id}")
def delete_server(
    server_id: int,
    db: Session = Depends(get_db)
):

    server = db.query(
        modules.Server
    ).filter(
        modules.Server.id == server_id
    ).first()

    if not server:

        return {
            "error": "Server not found"
        }

    db.delete(server)

    db.commit()

    return {
        "message": "Server deleted successfully",
        "server_id": server_id
    }


# =========================================================
# MONITOR SERVER
# =========================================================

@app.get("/servers/{server_id}/monitor")
def monitor_server(
    server_id: int,
    db: Session = Depends(get_db)
):

    server = db.query(
        modules.Server
    ).filter(
        modules.Server.id == server_id
    ).first()

    if not server:

        return {
            "error": "Server not found"
        }

    try:

        data = get_server_metrics(
            server.ip_address
        )

        server.status = "online"

        server.health_status = "healthy"

        server.cpu_usage = (
            data["cpu_usage_percent"]
        )

        server.ram_usage = (
            data["memory"]["usage_percent"]
        )

        server.disk_usage = float(
            data["disk"]["usage_percent"]
            .replace("%", "")
        )

        server.hostname = data["hostname"]

        server.uptime = data["uptime"]

        server.last_checked = datetime.utcnow()

        db.commit()

        db.refresh(server)

        return {

            "server_id": server.id,

            "name": server.name,

            "ip_address": server.ip_address,

            "status": server.status,

            "health_status": server.health_status,

            "hostname": server.hostname,

            "uptime": server.uptime,

            "cpu_usage": server.cpu_usage,

            "ram_usage": server.ram_usage,

            "disk_usage": server.disk_usage,

            "docker": data["docker"],

            "last_checked": server.last_checked

        }

    except Exception as e:

        server.status = "offline"

        server.health_status = "unhealthy"

        server.last_checked = datetime.utcnow()

        db.commit()

        return {

            "server_id": server.id,

            "status": "offline",

            "health_status": "unhealthy",

            "error": str(e)

        }


# =========================================================
# CREATE DEPLOYMENT
# =========================================================

@app.post("/deployments")
def create_deployment(
    server_id: int,
    application_name: str,
    repository_url: str,
    branch: str = "main",
    docker_image: str = "",
    container_name: str = "",
    port: int = 8000,
    db: Session = Depends(get_db)
):

    server = db.query(
        modules.Server
    ).filter(
        modules.Server.id == server_id
    ).first()

    if not server:

        return {
            "error": "Server not found"
        }

    # -----------------------------------------------------
    # DEFAULT DOCKER VALUES
    # -----------------------------------------------------

    if not docker_image:

        docker_image = (
            f"{application_name}:latest"
        )

    if not container_name:

        container_name = (
            f"opspilot-{application_name}"
        )

    # -----------------------------------------------------
    # CREATE DEPLOYMENT RECORD
    # -----------------------------------------------------

    deployment = modules.Deployment(

        server_id=server_id,

        application_name=application_name,

        repository_url=repository_url,

        branch=branch,

        docker_image=docker_image,

        container_name=container_name,

        port=port,

        status="running",

        started_at=datetime.utcnow()

    )

    db.add(deployment)

    server.deployment_status = "deploying"

    db.commit()

    db.refresh(deployment)

    # -----------------------------------------------------
    # ACTIVITY LOG
    # -----------------------------------------------------

    activity = modules.Activity(

        action="Deployment Created",

        description=(
            f"Deployment created for "
            f"{deployment.application_name}"
        ),

        entity_type="deployment",

        entity_id=deployment.id,

        status="success"

    )

    db.add(activity)

    db.commit()

    # -----------------------------------------------------
    # START BACKGROUND DEPLOYMENT
    # -----------------------------------------------------

    thread = threading.Thread(

        target=run_deployment,

        args=(deployment.id,),

        daemon=True

    )

    thread.start()

    return {

        "deployment_id": deployment.id,

        "server_id": server.id,

        "server_name": server.name,

        "application_name":
            deployment.application_name,

        "repository_url":
            deployment.repository_url,

        "branch":
            deployment.branch,

        "docker_image":
            deployment.docker_image,

        "container_name":
            deployment.container_name,

        "port":
            deployment.port,

        "status": "running",

        "message":
            "Deployment started automatically",

        "started_at":
            deployment.started_at

    }
# =========================================================
# GET ALL DEPLOYMENTS
# =========================================================

@app.get("/deployments")
def get_deployments(
    db: Session = Depends(get_db)
):

    deployments = db.query(
        modules.Deployment
    ).order_by(
        modules.Deployment.id.desc()
    ).all()

    result = []

    for deployment in deployments:

        server = db.query(
            modules.Server
        ).filter(
            modules.Server.id == deployment.server_id
        ).first()

        result.append({

            "id": deployment.id,

            "server_id": deployment.server_id,

            "server_name": (
                server.name
                if server
                else None
            ),

            "application_name":
                deployment.application_name,

            "repository_url":
                deployment.repository_url,

            "branch":
                deployment.branch,

            "docker_image":
                deployment.docker_image,

            "container_name":
                deployment.container_name,

            "port":
                deployment.port,

            "status":
                deployment.status,

            "started_at":
                deployment.started_at,

            "completed_at":
                deployment.completed_at,

            "output":
                deployment.output,

            "error_message":
                deployment.error_message

        })

    return result
# =========================================================
# GET SINGLE DEPLOYMENT
# =========================================================

@app.get("/deployments/{deployment_id}")
def get_deployment(
    deployment_id: int,
    db: Session = Depends(get_db)
):

    deployment = db.query(
        modules.Deployment
    ).filter(
        modules.Deployment.id == deployment_id
    ).first()

    if not deployment:

        return {
            "error": "Deployment not found"
        }

    server = db.query(
        modules.Server
    ).filter(
        modules.Server.id == deployment.server_id
    ).first()

    return {

        "deployment_id": deployment.id,

        "server_id": deployment.server_id,

        "server_name": (
            server.name
            if server
            else None
        ),

        "application_name":
            deployment.application_name,

        "repository_url":
            deployment.repository_url,

        "branch":
            deployment.branch,

        "docker_image":
            deployment.docker_image,

        "container_name":
            deployment.container_name,

        "port":
            deployment.port,

        "status":
            deployment.status,

        "started_at":
            deployment.started_at,

        "completed_at":
            deployment.completed_at,

        "output":
            deployment.output,

        "error_message":
            deployment.error_message

    }


# =========================================================
# DEPLOYMENT EXECUTION
# =========================================================

def run_deployment(deployment_id):

    db = SessionLocal()

    ssh = None

    try:

        # -------------------------------------------------
        # GET DEPLOYMENT
        # -------------------------------------------------

        deployment = db.query(
            modules.Deployment
        ).filter(
            modules.Deployment.id == deployment_id
        ).first()

        if not deployment:

            return

        # -------------------------------------------------
        # GET SERVER
        # -------------------------------------------------

        server = db.query(
            modules.Server
        ).filter(
            modules.Server.id == deployment.server_id
        ).first()

        if not server:

            deployment.status = "failed"

            deployment.error_message = (
                "Server not found"
            )

            deployment.completed_at = (
                datetime.utcnow()
            )

            db.commit()

            return

        try:

            # =================================================
            # SSH CONNECTION
            # =================================================

            ssh = connect_to_server(

                host=server.ip_address,

                username="ubuntu",

                key_path=r"C:\Users\hP\.ssh\id_ed25519"

            )

            print(
                f"[DEPLOYMENT] Connected to "
                f"{server.ip_address}"
            )

            # =================================================
            # APP DIRECTORY
            # =================================================

            app_dir = (
                f"/home/ubuntu/opspilot/"
                f"{deployment.application_name}"
            )

            # =================================================
            # DEPLOYMENT COMMANDS
            # =================================================

            commands = [

                "mkdir -p /home/ubuntu/opspilot",

                f"rm -rf {app_dir}",

                (
                    f"git clone -b "
                    f"{deployment.branch} "
                    f"{deployment.repository_url} "
                    f"{app_dir}"
                ),

                (
                    f"cd {app_dir} && "
                    f"docker build "
                    f"-t {deployment.docker_image} ."
                ),

                (
                    f"docker rm -f "
                    f"{deployment.container_name} "
                    f"2>/dev/null || true"
                ),

                (
                    f"docker run -d "
                    f"--name "
                    f"{deployment.container_name} "
                    f"-p {deployment.port}:8000 "
                    f"{deployment.docker_image}"
                )

            ]

            outputs = []

            # =================================================
            # RUN COMMANDS
            # =================================================

            for command in commands:

                print(
                    f"[DEPLOYMENT] Running: "
                    f"{command}"
                )

                result = run_command(

                    ssh,

                    command

                )

                output = result.get(
                    "output",
                    ""
                )

                error = result.get(
                    "error",
                    ""
                )
                exit_code = result.get(
                    "exit_code",
                    0
                )

                if error:
                    outputs.append(error)

                print(
                    f"[DEPLOYMENT OUTPUT] "
                    f"{output}"
                )

                if error:
                    print(
                        f"[DEPLOYMENT STDERR] "
                        f"{error}"
                    )

                if exit_code != 0:
                    raise Exception(
                        f"Command failed with exit code "
                        f"{exit_code}: {command}\n"
                        f"{error}"
                    )
            # =================================================
            # SUCCESS
            # =================================================

            deployment.status = "success"

            deployment.output = (
                "\n".join(outputs)
            )[-5000:]

            deployment.error_message = None

            deployment.completed_at = (
                datetime.utcnow()
            )

            server.deployment_status = "success"

            db.commit()


            # =================================================
            # ACTIVITY LOG - DEPLOYMENT SUCCESS
            # =================================================

            activity = modules.Activity(

                action="Deployment Successful",

                description=(
                    f"Deployment {deployment.application_name} "
                    f"completed successfully on server "
                    f"{server.name}"
                ),

                entity_type="deployment",

                entity_id=deployment.id,

                status="success"

            )

            db.add(activity)

            db.commit()


            print(
                f"[DEPLOYMENT SUCCESS] "
                f"{deployment.application_name}"
            )


        except Exception as e:

            # =================================================
            # FAILED
            # =================================================

            deployment.status = "failed"

            deployment.error_message = (
                str(e)
            )[-5000:]

            deployment.completed_at = (
                datetime.utcnow()
            )

            server.deployment_status = "failed"

            db.commit()


            # =================================================
            # ACTIVITY LOG - DEPLOYMENT FAILED
            # =================================================

            activity = modules.Activity(

                action="Deployment Failed",

                description=(
                    f"Deployment {deployment.application_name} "
                    f"failed on server "
                    f"{server.name}"
                ),

                entity_type="deployment",

                entity_id=deployment.id,

                status="failed"

            )

            db.add(activity)

            db.commit()


            print(
                f"[DEPLOYMENT FAILED] "
                f"{str(e)}"
            )


    except Exception as e:

        print(
            f"[DEPLOYMENT SYSTEM ERROR] "
            f"{str(e)}"
        )


    finally:

        if ssh:

            try:

                ssh.close()

            except Exception:

                pass

        db.close()

# =========================================================
# MANUAL DEPLOYMENT EXECUTION
# =========================================================

@app.post("/deployments/{deployment_id}/execute")
def execute_deployment(
    deployment_id: int,
    db: Session = Depends(get_db)
):

    deployment = db.query(
        modules.Deployment
    ).filter(
        modules.Deployment.id == deployment_id
    ).first()

    if not deployment:

        return {
            "error": "Deployment not found"
        }

    server = db.query(
        modules.Server
    ).filter(
        modules.Server.id == deployment.server_id
    ).first()

    if not server:

        return {
            "error": "Server not found"
        }

    if deployment.status == "running":

        return {

            "deployment_id":
                deployment.id,

            "status":
                "already_running",

            "message":
                "Deployment is already running"

        }

    deployment.status = "running"

    deployment.started_at = datetime.utcnow()

    deployment.completed_at = None

    deployment.output = None

    deployment.error_message = None

    server.deployment_status = "deploying"

    db.commit()

    thread = threading.Thread(

        target=run_deployment,

        args=(deployment.id,),

        daemon=True

    )

    thread.start()

    return {

        "deployment_id":
            deployment.id,

        "server_id":
            server.id,

        "server_name":
            server.name,

        "application_name":
            deployment.application_name,

        "status":
            "running",

        "message":
            "Deployment execution started"

    }

# =====================================================
# INCIDENT MANAGEMENT
# =====================================================

@app.post("/incidents")
def create_incident(
    server_id: int,
    title: str,
    description: str = None,
    severity: str = "medium",
    db: Session = Depends(get_db)
):
    server = db.query(
        modules.Server
    ).filter(
        modules.Server.id == server_id
    ).first()

    if not server:
        return {
            "error": "Server not found"
        }

    incident = modules.Incident(
        server_id=server_id,
        title=title,
        description=description,
        severity=severity,
        status="open",
        started_at=datetime.utcnow()
    )

    db.add(incident)

    server.deployment_status = "incident"

    db.commit()
    db.refresh(incident)

    activity = modules.Activity(
        action="Incident Created",
        description=(
            f"Incident {incident.title} created "
            f"on server {server.name}"
        ),
        entity_type="incident",
        entity_id=incident.id,
        status="success"
    )

    db.add(activity)
    db.commit()

    return {
        "incident_id": incident.id,
        "server_id": incident.server_id,
        "server_name": server.name,
        "title": incident.title,
        "severity": incident.severity,
        "status": incident.status,
        "started_at": incident.started_at,
        "message": "Incident created successfully"
    }


# =====================================================
# GET ALL INCIDENTS
# =====================================================

@app.get("/incidents")
def get_incidents(
    db: Session = Depends(get_db)
):
    incidents = db.query(
        modules.Incident
    ).order_by(
        modules.Incident.id.desc()
    ).all()

    result = []

    for incident in incidents:

        server = db.query(
            modules.Server
        ).filter(
            modules.Server.id == incident.server_id
        ).first()

        result.append({
            "id": incident.id,
            "server_id": incident.server_id,
            "server_name": server.name if server else None,
            "title": incident.title,
            "description": incident.description,
            "severity": incident.severity,
            "status": incident.status,
            "started_at": incident.started_at,
            "resolved_at": incident.resolved_at,
            "duration": incident.duration,
            "resolution": incident.resolution
        })

    return result


# =====================================================
# GET SINGLE INCIDENT
# =====================================================

@app.get("/incidents/{incident_id}")
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    incident = db.query(
        modules.Incident
    ).filter(
        modules.Incident.id == incident_id
    ).first()

    if not incident:
        return {
            "error": "Incident not found"
        }

    server = db.query(
        modules.Server
    ).filter(
        modules.Server.id == incident.server_id
    ).first()

    return {
        "id": incident.id,
        "server_id": incident.server_id,
        "server_name": server.name if server else None,
        "title": incident.title,
        "description": incident.description,
        "severity": incident.severity,
        "status": incident.status,
        "started_at": incident.started_at,
        "resolved_at": incident.resolved_at,
        "duration": incident.duration,
        "resolution": incident.resolution
    }


# =====================================================
# RESOLVE INCIDENT
# =====================================================

@app.put("/incidents/{incident_id}/resolve")
def resolve_incident(
    incident_id: int,
    resolution: str = None,
    db: Session = Depends(get_db)
):
    incident = db.query(
        modules.Incident
    ).filter(
        modules.Incident.id == incident_id
    ).first()

    if not incident:
        return {
            "error": "Incident not found"
        }

    if incident.status == "resolved":
        return {
            "error": "Incident already resolved"
        }

    incident.status = "resolved"
    incident.resolved_at = datetime.utcnow()
    incident.resolution = resolution

    if incident.started_at:
        duration_seconds = (
            incident.resolved_at -
            incident.started_at
        ).total_seconds()

        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)

        incident.duration = (
            f"{minutes}m {seconds}s"
        )

    server = db.query(
        modules.Server
    ).filter(
        modules.Server.id == incident.server_id
    ).first()

    if server:
        server.deployment_status = "success"

    db.commit()
    db.refresh(incident)

    activity = modules.Activity(
        action="Incident Resolved",
        description=(
            f"Incident {incident.title} resolved "
            f"on server {server.name}"
        ),
        entity_type="incident",
        entity_id=incident.id,
        status="success"
    )

    db.add(activity)
    db.commit()

    return {
        "incident_id": incident.id,
        "status": incident.status,
        "started_at": incident.started_at,
        "resolved_at": incident.resolved_at,
        "duration": incident.duration,
        "resolution": incident.resolution,
        "message": "Incident resolved successfully"
    }
# =====================================================
# ACTIVITY LOG
# =====================================================

@app.get("/activities")
def get_activities(
    db: Session = Depends(get_db)
):
    activities = db.query(
        modules.Activity
    ).order_by(
        modules.Activity.created_at.desc()
    ).all()

    return [
        {
            "id": activity.id,
            "action": activity.action,
            "description": activity.description,
            "entity_type": activity.entity_type,
            "entity_id": activity.entity_id,
            "status": activity.status,
            "created_at": activity.created_at
        }
        for activity in activities
    ]
# =====================================================
# DOCKER MONITORING
# =====================================================

@app.get("/servers/{server_id}/docker")
def get_server_docker(
    server_id: int,
    db: Session = Depends(get_db)
):
    server = db.query(
        modules.Server
    ).filter(
        modules.Server.id == server_id
    ).first()

    if not server:
        return {
            "error": "Server not found"
        }

    try:

        ssh = connect_to_server(
            host=server.ip_address,
            username="ubuntu",
            key_path=r"C:\Users\hP\.ssh\id_ed25519"
        )

        version_result = run_command(
            ssh,
            "docker --version"
        )

        containers_result = run_command(
            ssh,
            "docker ps -a --format '{{json .}}'"
        )

        images_result = run_command(
            ssh,
            "docker images --format '{{json .}}'"
        )

        ssh.close()

        return {
            "server_id": server.id,
            "server_name": server.name,
            "docker_version": version_result["output"],
            "containers": containers_result["output"],
            "images": images_result["output"]
        }

    except Exception as e:

        return {
            "server_id": server.id,
            "server_name": server.name,
            "error": str(e)
        }