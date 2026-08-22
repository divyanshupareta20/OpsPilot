from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime


class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    ip_address = Column(String(100), nullable=False)

    # Server status
    status = Column(String(50), default="unknown")
    health_status = Column(String(50), default="unknown")

    # Monitoring
    cpu_usage = Column(Float, default=0)
    ram_usage = Column(Float, default=0)
    disk_usage = Column(Float, default=0)

    # Server information
    os = Column(String(100), nullable=True)
    hostname = Column(String(100), nullable=True)
    uptime = Column(String(100), nullable=True)

    # Time tracking
    last_checked = Column(DateTime, nullable=True)
    last_started = Column(DateTime, nullable=True)
    last_stopped = Column(DateTime, nullable=True)

    # Deployment
    deployment_status = Column(String(50), default="unknown")


class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)

    server_id = Column(Integer, nullable=False)

    application_name = Column(String(100), nullable=False)

    repository_url = Column(String(500), nullable=True)

    branch = Column(String(100), default="main")

    docker_image = Column(String(200), nullable=True)

    container_name = Column(String(100), nullable=True)

    port = Column(Integer, nullable=True)

    status = Column(String(50), default="pending")

    started_at = Column(DateTime, nullable=True)

    completed_at = Column(DateTime, nullable=True)

    output = Column(String(5000), nullable=True)

    error_message = Column(String(5000), nullable=True)

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)

    server_id = Column(Integer, nullable=False)

    title = Column(String(200), nullable=False)

    description = Column(String(1000), nullable=True)

    severity = Column(String(50), default="medium")

    status = Column(String(50), default="open")

    started_at = Column(DateTime, nullable=True)

    resolved_at = Column(DateTime, nullable=True)

    duration = Column(String(100), nullable=True)

    resolution = Column(String(1000), nullable=True)

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)

    action = Column(String(100), nullable=False)

    description = Column(String(500), nullable=True)

    entity_type = Column(String(50), nullable=True)

    entity_id = Column(Integer, nullable=True)

    status = Column(String(50), default="success")

    created_at = Column(DateTime, default=datetime.utcnow)