"""Edge Multi-Spectral Computer Vision & 6D Grasp Affordance Estimator.

Simulates onboard edge neural inference (YOLOv8-Waste + PointNet 3D) running
on NVIDIA Jetson Orin Nano with multi-spectral NIR absorption classification.
"""
from __future__ import annotations
import math
import random
import time
from typing import List, Dict, Optional, Tuple
from app.schemas.physical_ai import MaterialClass, Point3D, DetectedObject


# Material classification lookup table with characteristic spectral absorption bands
SPECTRAL_SIGNATURES: Dict[MaterialClass, Dict[str, float]] = {
    MaterialClass.PET: {
        "nir_peak_nm": 1660.0,
        "transmissivity": 0.88,
        "density_g_cm3": 1.38,
        "default_bin": "BIN_1_PET_RECYCLE",
        "bin_x": 0.35, "bin_y": 0.20, "bin_z": -0.40,
    },
    MaterialClass.HDPE: {
        "nir_peak_nm": 1730.0,
        "transmissivity": 0.42,
        "density_g_cm3": 0.95,
        "default_bin": "BIN_2_HDPE_POLYMERS",
        "bin_x": 0.35, "bin_y": -0.20, "bin_z": -0.40,
    },
    MaterialClass.ALUMINUM_CAN: {
        "nir_peak_nm": 850.0,
        "transmissivity": 0.02,
        "density_g_cm3": 2.70,
        "default_bin": "BIN_3_METALS_ALUMINUM",
        "bin_x": -0.35, "bin_y": 0.20, "bin_z": -0.40,
    },
    MaterialClass.CARDBOARD: {
        "nir_peak_nm": 1450.0,
        "transmissivity": 0.10,
        "density_g_cm3": 0.68,
        "default_bin": "BIN_4_PAPER_CARDBOARD",
        "bin_x": -0.35, "bin_y": -0.20, "bin_z": -0.40,
    },
    MaterialClass.GLASS: {
        "nir_peak_nm": 2100.0,
        "transmissivity": 0.92,
        "density_g_cm3": 2.50,
        "default_bin": "BIN_5_GLASS_CULLET",
        "bin_x": 0.0, "bin_y": 0.35, "bin_z": -0.40,
    },
    MaterialClass.HAZARDOUS_EWASTE: {
        "nir_peak_nm": 1200.0,
        "transmissivity": 0.05,
        "density_g_cm3": 3.80,
        "default_bin": "BIN_6_HAZARDOUS_EWASTE",
        "bin_x": 0.0, "bin_y": -0.35, "bin_z": -0.40,
    },
}


class EdgeMultiSpectralPerception:
    """Multi-spectral computer vision perception pipeline for conveyor waste streams."""

    def __init__(self, camera_fps: int = 60, inference_latency_ms: float = 12.4):
        self.camera_fps = camera_fps
        self.inference_latency_ms = inference_latency_ms
        self.active_object_counter = 0

    def generate_synthetic_conveyor_stream(
        self,
        num_items: int = 15,
        conveyor_speed_m_s: float = 0.4,
        conveyor_y_start: float = -0.65,
    ) -> List[DetectedObject]:
        """Generates synthetic waste items positioned along conveyor upstream of delta robot."""
        materials = [
            MaterialClass.PET,
            MaterialClass.HDPE,
            MaterialClass.ALUMINUM_CAN,
            MaterialClass.CARDBOARD,
            MaterialClass.GLASS,
            MaterialClass.HAZARDOUS_EWASTE,
        ]
        # Distribution weights reflecting Indian municipal dry waste streams
        weights = [0.35, 0.25, 0.15, 0.15, 0.05, 0.05]

        detected_items: List[DetectedObject] = []
        current_y = conveyor_y_start

        for i in range(num_items):
            self.active_object_counter += 1
            mat = random.choices(materials, weights=weights)[0]
            spec = SPECTRAL_SIGNATURES[mat]

            # Conveyor lateral distribution x in [-0.18, +0.18] meters
            obj_x = random.uniform(-0.16, 0.16)
            # Spacing between consecutive items on conveyor (0.15m to 0.35m)
            current_y += random.uniform(0.18, 0.32)
            obj_y = current_y
            # Belt surface height z = -0.52m with item thickness 0.02 - 0.08m
            thickness = random.uniform(0.025, 0.065)
            obj_z = -0.520 + thickness

            # Grasp affordance score based on surface flatness and orientation
            yaw = random.uniform(-math.pi / 2, math.pi / 2)
            grasp_score = self.evaluate_grasp_affordance(mat, thickness, yaw)
            confidence = random.uniform(0.92, 0.99)
            mass_kg = random.uniform(0.020, 0.180)

            # 2D Bounding box simulation [ymin, xmin, ymax, xmax]
            cx, cy = 0.5 + (obj_x / 0.5) * 0.4, 0.5 + (obj_y / 0.8) * 0.4
            bw, bh = random.uniform(0.08, 0.14), random.uniform(0.08, 0.14)
            bbox = [
                max(0.0, cy - bh / 2),
                max(0.0, cx - bw / 2),
                min(1.0, cy + bh / 2),
                min(1.0, cx + bw / 2),
            ]

            target_bin = spec["default_bin"]
            bin_coords = Point3D(x=spec["bin_x"], y=spec["bin_y"], z=spec["bin_z"])

            detected_items.append(
                DetectedObject(
                    object_id=f"OBJ-{self.active_object_counter:04d}",
                    material=mat,
                    confidence=round(confidence, 3),
                    spectral_nir_peak_nm=spec["nir_peak_nm"] + random.uniform(-5.0, 5.0),
                    position=Point3D(x=round(obj_x, 3), y=round(obj_y, 3), z=round(obj_z, 3)),
                    bounding_box_2d=[round(c, 3) for c in bbox],
                    orientation_rad=round(yaw, 3),
                    mass_kg=round(mass_kg, 3),
                    grasp_quality=round(grasp_score, 3),
                    designated_bin=target_bin,
                    target_bin_coords=bin_coords,
                )
            )

        return detected_items

    def evaluate_grasp_affordance(self, material: MaterialClass, thickness: float, yaw: float) -> float:
        """Calculates robotic vacuum/pneumatic grasp affordance score Q in [0, 1]."""
        # Flat plastics & cardboard offer high suction seal quality
        base_quality = {
            MaterialClass.PET: 0.94,
            MaterialClass.HDPE: 0.91,
            MaterialClass.ALUMINUM_CAN: 0.88,
            MaterialClass.CARDBOARD: 0.92,
            MaterialClass.GLASS: 0.82,
            MaterialClass.HAZARDOUS_EWASTE: 0.79,
        }[material]

        # Geometry penalty for extreme tilts
        orientation_penalty = abs(yaw) / (math.pi / 2.0) * 0.08
        thickness_factor = 0.05 if thickness > 0.05 else 0.0

        q = base_quality - orientation_penalty + thickness_factor + random.uniform(-0.03, 0.02)
        return max(0.50, min(0.99, q))
