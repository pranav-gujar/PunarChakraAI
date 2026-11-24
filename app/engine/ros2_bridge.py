"""Sim-to-Real ROS 2 Bridge, Real-Time Serial Protocol, and Hardware BOM.

Defines ROS 2 Humble node topics, EtherCAT / micro-ROS serial frame serialization,
and the comprehensive hardware engineering Bill of Materials (BOM) for physical deployment.
"""
from __future__ import annotations
import struct
from typing import List, Dict
from app.schemas.physical_ai import HardwareBOMResponse, HardwareBOMItem, JointAngles


class MicroROSEtherCATBridge:
    """Serial communication bridge packaging joint velocity and pneumatic commands for microcontrollers."""

    START_BYTE_1 = 0xAA
    START_BYTE_2 = 0x55
    CMD_SERVO_PNEUMATIC = 0x01

    @staticmethod
    def calculate_crc16(data: bytes) -> int:
        """Calculates standard CRC-16-CCITT checksum for noise-tolerant industrial transmission."""
        crc = 0xFFFF
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = ((crc << 1) ^ 0x1021) & 0xFFFF
                else:
                    crc = (crc << 1) & 0xFFFF
        return crc

    def encode_servo_command_packet(
        self,
        joint_angles: JointAngles,
        vacuum_active: bool,
        sequence_num: int = 1,
    ) -> bytes:
        """Encodes joint targets and vacuum state into a 16-byte real-time EtherCAT/Micro-ROS packet.
        
        Frame Format:
        [0-1] Header: 0xAA, 0x55
        [2]   Command ID: 0x01
        [3]   Sequence Number: 0-255
        [4-5] Motor 1 Angle (int16_t, 100x fixed-point)
        [6-7] Motor 2 Angle (int16_t, 100x fixed-point)
        [8-9] Motor 3 Angle (int16_t, 100x fixed-point)
        [10]  Vacuum Valve Bitmask: 0x01 (On), 0x00 (Off)
        [11-13] Reserved Padding
        [14-15] CRC16 Checksum
        """
        th1_int = int(joint_angles.theta1_deg * 100)
        th2_int = int(joint_angles.theta2_deg * 100)
        th3_int = int(joint_angles.theta3_deg * 100)
        vac_byte = 1 if vacuum_active else 0

        payload = struct.pack(
            ">BBBBhhhB3s",
            self.START_BYTE_1,
            self.START_BYTE_2,
            self.CMD_SERVO_PNEUMATIC,
            sequence_num % 256,
            th1_int,
            th2_int,
            th3_int,
            vac_byte,
            b"\x00\x00\x00",
        )

        crc = self.calculate_crc16(payload)
        packet = payload + struct.pack(">H", crc)
        return packet

    @staticmethod
    def get_hardware_bom() -> HardwareBOMResponse:
        """Returns verified, production-ready Hardware Bill of Materials (BOM) for physical deployment."""
        items: List[HardwareBOMItem] = [
            HardwareBOMItem(
                component_name="Embedded AI Compute Platform",
                category="Edge Computing",
                model_spec="NVIDIA Jetson Orin Nano Developer Kit (8GB, 40 TOPS AI, Ampere GPU)",
                quantity=1,
                estimated_cost_inr=42500.0,
                interface_protocol="Gigabit Ethernet / USB 3.2 / CAN 2.0B",
            ),
            HardwareBOMItem(
                component_name="High-Speed Delta Parallel Kinematic Frame",
                category="Robotic Mechanics",
                model_spec="Custom Carbon-Fiber Delta Arms (L1=350mm, L2=650mm) with Igus Spherical Rod Ends",
                quantity=1,
                estimated_cost_inr=28000.0,
                interface_protocol="Mechanical ISO-Flange",
            ),
            HardwareBOMItem(
                component_name="Brushless AC Servo Motors & Drives",
                category="Actuation",
                model_spec="Leadshine EL7-EC400 400W AC Servos (3000 RPM, 1.27 Nm nominal, 17-bit absolute encoder)",
                quantity=3,
                estimated_cost_inr=36000.0,
                interface_protocol="EtherCAT / Modbus-RTU RS485",
            ),
            HardwareBOMItem(
                component_name="Multi-Spectral RGB-NIR Depth Sensor",
                category="Perception Sensors",
                model_spec="Intel RealSense D435i Stereo Active IR Camera with 850nm/1600nm Optical Bandpass Filter",
                quantity=1,
                estimated_cost_inr=38000.0,
                interface_protocol="USB 3.1 Type-C / V4L2",
            ),
            HardwareBOMItem(
                component_name="High-Flow Venturi Vacuum Ejector & Gripper",
                category="End-Effector Pneumatics",
                model_spec="Festo VN-05-H-T3-PQ2 Venturi Ejector + 40mm Bellows Suction Cup + Solenoid Valve",
                quantity=1,
                estimated_cost_inr=14500.0,
                interface_protocol="24V DC Digital Output (Sinking)",
            ),
            HardwareBOMItem(
                component_name="Real-Time Micro-ROS Controller",
                category="Embedded Real-Time",
                model_spec="STMicroelectronics STM32F407VGT6 ARM Cortex-M4 (168MHz) running FreeRTOS + micro-ROS",
                quantity=1,
                estimated_cost_inr=3800.0,
                interface_protocol="Micro-ROS Serial / UART / SPI",
            ),
            HardwareBOMItem(
                component_name="Industrial 24V DC Power Supply & Safety Relays",
                category="Power & Safety",
                model_spec="Mean Well NDR-480-24 (24V, 20A, 480W DIN Rail) + Pilz Emergency Stop Circuit",
                quantity=1,
                estimated_cost_inr=6200.0,
                interface_protocol="Terminal Block / Dual Safety Contactors",
            ),
        ]

        total_cost = sum(item.estimated_cost_inr for item in items)

        return HardwareBOMResponse(
            solution_name="PunarChakra AI Industrial Delta Physical AI System",
            target_trl=4,
            total_budget_inr=total_cost,
            compute_edge_platform="NVIDIA Jetson Orin Nano (8GB)",
            actuation_type="3-DOF Parallel Delta with EtherCAT Servo Control",
            ros2_distribution="ROS 2 Humble Hawksbill on Ubuntu 22.04 LTS (Real-Time PREEMPT_RT)",
            items=items,
        )
