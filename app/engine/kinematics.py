"""Delta Parallel Robot 3-DOF Analytical Kinematics & Workspace Validator.

Implements closed-form Inverse Kinematics (IK), Forward Kinematics (FK),
Jacobian matrix calculation, and singularity detection for industrial sorting delta robots.
"""
from __future__ import annotations
import math
from typing import Tuple, Optional, Dict
import numpy as np


class DeltaKinematics:
    """Analytical Kinematics Solver for a 3-DOF Parallel Delta Robot."""

    def __init__(
        self,
        base_radius: float = 0.250,        # R_b: Base platform radius (meters)
        end_effector_radius: float = 0.050, # R_p: Moving end-effector platform radius (meters)
        bicep_length: float = 0.350,       # L_1: Upper bicep arm length (meters)
        forearm_length: float = 0.650,     # L_2: Lower parallelogram forearm rod length (meters)
    ):
        self.r_b = base_radius
        self.r_p = end_effector_radius
        self.l1 = bicep_length
        self.l2 = forearm_length

        # Effective offset (base radius minus platform radius)
        self.r_eff = self.r_b - self.r_p

        # Arm orientation angles in base XY plane (120 degrees apart)
        self.phi_deg = [0.0, 120.0, 240.0]
        self.phi_rad = [math.radians(deg) for deg in self.phi_deg]

    def inverse_kinematics(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """Calculates joint angles [theta1, theta2, theta3] in degrees for Cartesian end-effector position (x, y, z).
        
        Args:
            x, y, z: Position in meters relative to base center. Note: z is negative downwards.
            
        Returns:
            Tuple of (theta1, theta2, theta3) in degrees.
            
        Raises:
            ValueError: If position (x, y, z) is outside reachable workspace.
        """
        thetas = []

        for i, phi in enumerate(self.phi_rad):
            # Rotate Cartesian coordinates into the 2D plane of arm i
            x_prime = x * math.cos(phi) + y * math.sin(phi)
            y_prime = -x * math.sin(phi) + y * math.cos(phi)
            z_prime = z

            # Coefficients of circle-sphere intersection equation:
            # a * cos(theta) + b * sin(theta) + c = 0
            dx = x_prime - self.r_eff
            a = 2.0 * self.l1 * dx
            b = 2.0 * self.l1 * z_prime
            c = (dx ** 2) + (y_prime ** 2) + (z_prime ** 2) + (self.l1 ** 2) - (self.l2 ** 2)

            # Weierstrass substitution: t = tan(theta/2)
            # (c - a) * t^2 + 2 * b * t + (c + a) = 0
            discriminant = (a ** 2) + (b ** 2) - (c ** 2)

            if discriminant < 0:
                raise ValueError(
                    f"Position ({x:.3f}, {y:.3f}, {z:.3f}) is outside Delta workspace for arm {i+1} (disc={discriminant:.4f})."
                )

            # Choose the lower / elbow-down physically feasible branch
            sqrt_disc = math.sqrt(max(0.0, discriminant))
            t1 = (-b - sqrt_disc) / (c - a) if abs(c - a) > 1e-9 else -c / (2.0 * b)
            theta_rad = 2.0 * math.atan(t1)
            theta_deg = math.degrees(theta_rad)

            thetas.append(theta_deg)

        return thetas[0], thetas[1], thetas[2]

    def forward_kinematics(self, theta1_deg: float, theta2_deg: float, theta3_deg: float) -> Tuple[float, float, float]:
        """Computes Cartesian position (x, y, z) from joint angles using geometric trilateration of 3 spheres."""
        thetas = [math.radians(t) for t in (theta1_deg, theta2_deg, theta3_deg)]
        elbows = []

        for i, (phi, th) in enumerate(zip(self.phi_rad, thetas)):
            # Elbow coordinate in rotated frame
            ex_prime = self.r_eff + self.l1 * math.cos(th)
            ez_prime = self.l1 * math.sin(th)
            ey_prime = 0.0

            # Transform back to base world frame
            wx = ex_prime * math.cos(phi) - ey_prime * math.sin(phi)
            wy = ex_prime * math.sin(phi) + ey_prime * math.cos(phi)
            wz = ez_prime
            elbows.append(np.array([wx, wy, wz]))

        # The end effector is at the intersection of 3 spheres of radius l2 centered at elbows[0], elbows[1], elbows[2]
        p1, p2, p3 = elbows[0], elbows[1], elbows[2]
        
        # Standard trilateration
        ex = (p2 - p1) / np.linalg.norm(p2 - p1)
        i_dot = np.dot(ex, p3 - p1)
        ey = (p3 - p1 - i_dot * ex) / np.linalg.norm(p3 - p1 - i_dot * ex)
        ez = np.cross(ex, ey)
        d = np.linalg.norm(p2 - p1)
        j_dot = np.dot(ey, p3 - p1)

        x_local = ((self.l2 ** 2) - (self.l2 ** 2) + (d ** 2)) / (2 * d)
        y_local = (((self.l2 ** 2) - (self.l2 ** 2) + (i_dot ** 2) + (j_dot ** 2)) / (2 * j_dot)) - ((i_dot / j_dot) * x_local)
        
        z_sq = (self.l2 ** 2) - (x_local ** 2) - (y_local ** 2)
        if z_sq < 0:
            raise ValueError("No physical forward kinematics solution for given joint angles.")
        z_local = -math.sqrt(z_sq) # Working downward hemisphere

        tri_sol = p1 + x_local * ex + y_local * ey + z_local * ez
        return float(tri_sol[0]), float(tri_sol[1]), float(tri_sol[2])

    def compute_jacobian(self, x: float, y: float, z: float) -> np.ndarray:
        """Computes the 3x3 kinematic Jacobian J where V_cartesian = J * omega_joints."""
        th1, th2, th3 = self.inverse_kinematics(x, y, z)
        thetas_deg = [th1, th2, th3]
        eps = 1e-4
        
        # Numerical finite-difference Jacobian approximation for rock-solid stability
        J = np.zeros((3, 3))
        for j in range(3):
            th_perturbed = list(thetas_deg)
            th_perturbed[j] += eps
            x_p, y_p, z_p = self.forward_kinematics(th_perturbed[0], th_perturbed[1], th_perturbed[2])
            J[0, j] = (x_p - x) / math.radians(eps)
            J[1, j] = (y_p - y) / math.radians(eps)
            J[2, j] = (z_p - z) / math.radians(eps)

        return J

    def manipulability_index(self, x: float, y: float, z: float) -> float:
        """Calculates Yoshikawa's manipulability measure w = sqrt(det(J * J^T))."""
        try:
            J = self.compute_jacobian(x, y, z)
            JJt = np.dot(J, J.T)
            det = np.linalg.det(JJt)
            return float(math.sqrt(max(0.0, det)))
        except Exception:
            return 0.0

    def is_within_workspace(self, x: float, y: float, z: float) -> bool:
        """Quick bounds check for delta arm operational envelope."""
        # Standard delta cylinder: radius ~0.35m, z in [-0.75m, -0.35m]
        radial_dist = math.hypot(x, y)
        if radial_dist > 0.42 or z < -0.80 or z > -0.25:
            return False
        try:
            th1, th2, th3 = self.inverse_kinematics(x, y, z)
            # Motor range: -45 deg to +95 deg
            for th in (th1, th2, th3):
                if th < -45.0 or th > 105.0:
                    return False
            return True
        except ValueError:
            return False
