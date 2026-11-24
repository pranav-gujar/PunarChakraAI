from __future__ import annotations
from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class MaterialClass(str, Enum):
    PET = "PET"                  # Polyethylene terephthalate (transparent drink bottles)
    HDPE = "HDPE"                # High-density polyethylene (milk jugs, shampoo)
    ALUMINUM_CAN = "ALUMINUM"    # Beverage cans, tins
    CARDBOARD = "CARDBOARD"      # Corrugated cardboard boxes, dry packaging
    GLASS = "GLASS"              # Glass bottles (amber, green, flint)
    HAZARDOUS_EWASTE = "EWASTE"  # Batteries, PCB fragments, electronic scrap


class Point3D(BaseModel):
    x: float = Field(..., description="X coordinate in meters (conveyor lateral)")
    y: float = Field(..., description="Y coordinate in meters (conveyor longitudinal/flow)")
    z: float = Field(..., description="Z coordinate in meters (vertical, negative downwards from base)")


class JointAngles(BaseModel):
    theta1_deg: float = Field(..., description="Motor 1 joint angle in degrees")
    theta2_deg: float = Field(..., description="Motor 2 joint angle in degrees")
    theta3_deg: float = Field(..., description="Motor 3 joint angle in degrees")


class DetectedObject(BaseModel):
    object_id: str
    material: MaterialClass
    confidence: float = Field(..., ge=0.0, le=1.0)
    spectral_nir_peak_nm: float
    position: Point3D
    bounding_box_2d: List[float] = Field(..., description="[ymin, xmin, ymax, xmax] in normalized pixels")
    orientation_rad: float = Field(..., description="Planar yaw rotation in radians")
    mass_kg: float = Field(..., description="Estimated mass in kilograms")
    grasp_quality: float = Field(..., ge=0.0, le=1.0, description="Surface normal and flatness affordance score")
    designated_bin: str
    target_bin_coords: Point3D


class TrajectoryWaypoint(BaseModel):
    time_offset_s: float
    position: Point3D
    velocity: Point3D
    joint_angles: JointAngles
    gripper_vacuum_active: bool
    phase_label: str


class TrajectoryPlan(BaseModel):
    plan_id: str
    object_id: str
    total_duration_s: float
    sample_rate_hz: int
    waypoints: List[TrajectoryWaypoint]
    max_acceleration_m_s2: float
    estimated_energy_joules: float


class SimulationEpisodeResult(BaseModel):
    episode_id: str
    objects_generated: int
    objects_detected: int
    objects_picked: int
    missed_objects: int
    purity_rate_percent: float
    pick_success_rate_percent: float
    average_cycle_time_ms: float
    throughput_picks_per_min: float
    total_energy_consumed_joules: float
    sim_to_real_gap_score: float
    material_breakdown: Dict[str, int]


class HardwareBOMItem(BaseModel):
    component_name: str
    category: str
    model_spec: str
    quantity: int
    estimated_cost_inr: float
    interface_protocol: str


class HardwareBOMResponse(BaseModel):
    solution_name: str
    target_trl: int
    total_budget_inr: float
    compute_edge_platform: str
    actuation_type: str
    ros2_distribution: str
    items: List[HardwareBOMItem]
