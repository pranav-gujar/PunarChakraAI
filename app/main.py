"""PunarChakra AI - FastAPI Application Server and Physical AI Control Hub."""
from __future__ import annotations
import os
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

from app.schemas.physical_ai import (
    Point3D,
    JointAngles,
    DetectedObject,
    TrajectoryPlan,
    SimulationEpisodeResult,
    HardwareBOMResponse,
)
from app.engine.kinematics import DeltaKinematics
from app.engine.perception import EdgeMultiSpectralPerception
from app.engine.trajectory_planner import QuinticTrajectoryPlanner
from app.engine.physics_sim import PhysicalSimulationBench
from app.engine.ros2_bridge import MicroROSEtherCATBridge

app = FastAPI(
    title="PunarChakra AI - Physical AI Sorting Controller",
    description="From Simulation to Reality: High-Speed Parallel Delta Autonomous Waste Segregation System",
    version="1.0.0",
)

# Initialize core robotic engines
kinematics = DeltaKinematics()
perception = EdgeMultiSpectralPerception()
planner = QuinticTrajectoryPlanner(kinematics)
simulation_bench = PhysicalSimulationBench()
ros2_bridge = MicroROSEtherCATBridge()

# Setup templates and static directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """Serves the interactive Physical AI Delta Robot Command Center."""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/api/health")
async def health_check():
    """Health check endpoint for ROS2 bridge and system status."""
    return {
        "status": "online",
        "system": "PunarChakra AI Physical Sorting Engine",
        "ros2_node": "/punarchakra/delta_controller",
        "realtime_kernel": "PREEMPT_RT",
        "edge_accelerator": "NVIDIA Jetson Orin Nano (TensorRT)",
        "trl_level": 4,
    }


@app.post("/api/kinematics/inverse", response_model=JointAngles)
async def compute_inverse_kinematics(point: Point3D):
    """Calculates motor angles (theta1, theta2, theta3) for Cartesian position (x, y, z)."""
    try:
        th1, th2, th3 = kinematics.inverse_kinematics(point.x, point.y, point.z)
        return JointAngles(
            theta1_deg=round(th1, 2),
            theta2_deg=round(th2, 2),
            theta3_deg=round(th3, 2),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/kinematics/forward", response_model=Point3D)
async def compute_forward_kinematics(angles: JointAngles):
    """Computes Cartesian position (x, y, z) from joint angles."""
    try:
        x, y, z = kinematics.forward_kinematics(
            angles.theta1_deg, angles.theta2_deg, angles.theta3_deg
        )
        return Point3D(x=round(x, 4), y=round(y, 4), z=round(z, 4))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/perception/stream", response_model=List[DetectedObject])
async def get_conveyor_perception_stream(num_items: int = 12):
    """Simulates real-time multi-spectral camera perception on moving conveyor."""
    return perception.generate_synthetic_conveyor_stream(num_items=num_items)


@app.post("/api/trajectory/plan", response_model=TrajectoryPlan)
async def generate_trajectory_plan(obj: DetectedObject):
    """Generates quintic minimum-jerk trajectory with moving conveyor compensation."""
    return planner.plan_pick_and_place(obj)


@app.post("/api/simulate", response_model=SimulationEpisodeResult)
async def run_simulation(
    num_items: int = 50,
    conveyor_speed: float = 0.40,
    domain_randomization: bool = True,
):
    """Executes a full rigid-body physics simulation episode with domain randomization."""
    result, _, _ = simulation_bench.run_simulation_episode(
        num_items=num_items,
        conveyor_nominal_speed=conveyor_speed,
        enable_domain_randomization=domain_randomization,
    )
    return result


@app.get("/api/hardware-bom", response_model=HardwareBOMResponse)
async def get_hardware_bom():
    """Returns the verified hardware engineering bill of materials for physical deployment."""
    return ros2_bridge.get_hardware_bom()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
