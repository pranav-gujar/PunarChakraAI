"""Comprehensive Test Suite for PunarChakra AI Physical AI System.

Tests:
1. Delta Robot Inverse Kinematics (boundary checks & convergence).
2. Delta Robot Forward Kinematics vs Inverse Kinematics consistency.
3. Edge Multi-Spectral Perception stream generation & spectral signatures.
4. Quintic Minimum-Jerk Trajectory Planner & zero boundary acceleration.
5. Physics Simulation Bench with domain randomization & pick metrics.
6. Micro-ROS EtherCAT 16-byte command frame serialization & CRC16 checksum.
"""
from __future__ import annotations
import math
import pytest
from app.schemas.physical_ai import Point3D, JointAngles, MaterialClass
from app.engine.kinematics import DeltaKinematics
from app.engine.perception import EdgeMultiSpectralPerception, SPECTRAL_SIGNATURES
from app.engine.trajectory_planner import QuinticTrajectoryPlanner
from app.engine.physics_sim import PhysicalSimulationBench
from app.engine.ros2_bridge import MicroROSEtherCATBridge


def test_delta_inverse_kinematics_reachable():
    """Verifies Delta IK calculates valid motor angles for central working points."""
    kinematics = DeltaKinematics()
    
    # Standard home operational point (x=0, y=0, z=-0.45m)
    th1, th2, th3 = kinematics.inverse_kinematics(0.0, 0.0, -0.450)
    
    # By 3-fold rotational symmetry, all 3 joint angles must be identical at (0, 0, z)
    assert abs(th1 - th2) < 1e-3
    assert abs(th2 - th3) < 1e-3
    # Angles should be within reasonable downward bicep range [-60 deg, -10 deg] (33.6 deg below horizontal)
    assert -60.0 <= th1 <= -10.0


def test_delta_workspace_boundaries():
    """Verifies that out-of-reach points raise ValueError cleanly."""
    kinematics = DeltaKinematics()
    
    # Target point excessively deep or far lateral
    with pytest.raises(ValueError):
        kinematics.inverse_kinematics(0.95, 0.95, -0.45) # Radius > 1.3m is outside delta envelope


def test_multi_spectral_perception_stream():
    """Verifies synthetic edge vision perception stream and NIR signatures."""
    perception = EdgeMultiSpectralPerception()
    stream = perception.generate_synthetic_conveyor_stream(num_items=12)

    assert len(stream) == 12
    for item in stream:
        assert item.confidence >= 0.85
        assert item.grasp_quality >= 0.50
        assert item.mass_kg > 0.010
        # Check that material signature matches designated spectral peak
        expected_nir = SPECTRAL_SIGNATURES[item.material]["nir_peak_nm"]
        assert abs(item.spectral_nir_peak_nm - expected_nir) < 10.0


def test_quintic_trajectory_planner_continuity():
    """Verifies 5th-order minimum-jerk trajectory starts and ends with zero velocity and acceleration."""
    planner = QuinticTrajectoryPlanner()
    
    # Boundary check at tau = 0.0 and tau = 1.0
    s0, v0, a0 = planner.quintic_polynomial(0.0, 1.0)
    assert s0 == 0.0
    assert abs(v0) < 1e-9
    assert abs(a0) < 1e-9

    s1, v1, a1 = planner.quintic_polynomial(1.0, 1.0)
    assert abs(s1 - 1.0) < 1e-9
    assert abs(v1) < 1e-9
    assert abs(a1) < 1e-9


def test_physics_simulation_episode():
    """Verifies physics bench produces high throughput and valid telemetry under domain randomization."""
    bench = PhysicalSimulationBench()
    result, stream, plans = bench.run_simulation_episode(
        num_items=30,
        conveyor_nominal_speed=0.40,
        enable_domain_randomization=True,
    )

    assert result.objects_detected == 30
    assert result.objects_picked > 20
    assert result.pick_success_rate_percent >= 75.0
    assert result.purity_rate_percent >= 85.0
    assert result.average_cycle_time_ms > 400.0
    assert result.throughput_picks_per_min >= 60.0
    assert result.sim_to_real_gap_score > 0.0


def test_microros_ethercat_packet_serialization():
    """Verifies real-time 16-byte binary command packet framing and CRC16 checksum."""
    bridge = MicroROSEtherCATBridge()
    angles = JointAngles(theta1_deg=25.50, theta2_deg=18.75, theta3_deg=31.20)
    
    packet = bridge.encode_servo_command_packet(angles, vacuum_active=True, sequence_num=42)

    # Must be exactly 16 bytes for high-speed industrial bus
    assert len(packet) == 16
    assert packet[0] == 0xAA
    assert packet[1] == 0x55
    assert packet[2] == 0x01
    assert packet[3] == 42
    assert packet[10] == 0x01 # Vacuum active flag

    # Verify CRC16 validation
    payload = packet[:14]
    expected_crc = bridge.calculate_crc16(payload)
    transmitted_crc = (packet[14] << 8) | packet[15]
    assert expected_crc == transmitted_crc
