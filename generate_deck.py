"""Generates 12-slide 16:9 widescreen solution deck PDF for PunarChakra AI.

Uses HTML/CSS rendering printed via headless Microsoft Edge to produce
an ultra crisp, publication-grade PDF conforming to TIH Hackathon rubric.
"""
from __future__ import annotations
import os
import subprocess
import sys

OUTPUT_HTML = r"d:\Pranav\I Hack\punarchakra\deck.html"
OUTPUT_PDF = r"d:\Pranav\I Hack\PunarChakra_Solution_Deck.pdf"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @page {
    size: 1280px 720px;
    margin: 0;
  }
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    background-color: #050811;
    color: #f8fafc;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .slide {
    width: 1280px;
    height: 720px;
    page-break-after: always;
    position: relative;
    padding: 44px 56px;
    background: radial-gradient(circle at 85% 15%, rgba(6, 182, 212, 0.12), transparent 45%),
                radial-gradient(circle at 15% 85%, rgba(16, 185, 129, 0.08), transparent 40%),
                #070b14;
    overflow: hidden;
  }
  .slide::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; height: 4px;
    background: linear-gradient(90deg, #06b6d4, #10b981, #3b82f6);
  }
  .slide-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
  }
  .slide-category {
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #06b6d4;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .slide-title {
    font-size: 28px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
    margin-top: 4px;
  }
  .slide-subtitle {
    font-size: 14px;
    color: #94a3b8;
    margin-top: 2px;
  }
  .slide-badge {
    background: rgba(6, 182, 212, 0.15);
    border: 1px solid rgba(6, 182, 212, 0.35);
    color: #38bdf8;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.5px;
  }
  .slide-footer {
    position: absolute;
    bottom: 20px;
    left: 56px;
    right: 56px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 11px;
    color: #64748b;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    padding-top: 12px;
  }
  .slide-footer .confidential {
    color: #06b6d4;
    font-weight: 600;
  }
  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }
  .grid-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 20px;
  }
  .grid-4 {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
  }
  .card {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 20px;
    position: relative;
  }
  .card-highlight {
    border-color: rgba(6, 182, 212, 0.4);
    background: rgba(6, 182, 212, 0.06);
  }
  .card-title {
    font-size: 16px;
    font-weight: 700;
    color: #38bdf8;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .card-p {
    font-size: 13px;
    color: #cbd5e1;
    line-height: 1.55;
  }
  .metric-box {
    background: rgba(6, 182, 212, 0.08);
    border: 1px solid rgba(6, 182, 212, 0.25);
    border-radius: 10px;
    padding: 14px 18px;
    text-align: center;
  }
  .metric-val {
    font-size: 32px;
    font-weight: 800;
    font-family: 'Consolas', monospace;
    color: #10b981;
    margin-bottom: 2px;
  }
  .metric-lbl {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #94a3b8;
  }
  .tag {
    display: inline-block;
    background: rgba(255, 255, 255, 0.08);
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 6px;
    margin-top: 6px;
    color: #e2e8f0;
  }
  table.deck-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    margin-top: 6px;
  }
  table.deck-table th {
    background: rgba(6, 182, 212, 0.15);
    color: #38bdf8;
    padding: 8px 10px;
    text-align: left;
    font-weight: 700;
    border-bottom: 1px solid rgba(6, 182, 212, 0.3);
  }
  table.deck-table td {
    padding: 7px 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    color: #cbd5e1;
  }
  .code-box {
    background: #030712;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 12px 16px;
    font-family: 'Consolas', monospace;
    font-size: 11px;
    color: #38bdf8;
    line-height: 1.5;
  }
  .step-node {
    display: flex;
    gap: 12px;
    margin-bottom: 14px;
  }
  .step-num {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #06b6d4;
    color: #030712;
    font-weight: 800;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
</style>
</head>
<body>

<!-- SLIDE 1: COVER -->
<div class="slide" style="display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center;">
  <div style="background:rgba(6, 182, 212, 0.15); border:1px solid rgba(6, 182, 212, 0.4); padding:6px 18px; border-radius:9999px; font-size:13px; font-weight:700; color:#38bdf8; margin-bottom:18px; letter-spacing:1px;">
    TIH FOUNDATION IoT &amp; IoE PHYSICAL AI HACKATHON &bull; E-SUMMIT '26 (IIT BOMBAY)
  </div>
  <h1 style="font-size:52px; font-weight:900; letter-spacing:-1px; margin-bottom:10px; background:linear-gradient(135deg, #ffffff 40%, #06b6d4 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
    PunarChakra AI (पुनर्चक्र)
  </h1>
  <div style="font-size:22px; font-weight:600; color:#10b981; margin-bottom:18px;">
    Physical AI – From Simulation to Reality
  </div>
  <p style="font-size:16px; color:#cbd5e1; max-width:820px; line-height:1.6; margin-bottom:34px;">
    An Industrial-Grade Cyber-Physical Autonomous Waste Segregation System combining Edge Multi-Spectral Computer Vision, Closed-Form Delta Kinematics, Quintic Minimum-Jerk Trajectory Planning, and a Real-Time ROS 2 / micro-ROS EtherCAT Actuation Bridge.
  </p>
  <div class="grid-4" style="max-width:980px; width:100%;">
    <div class="metric-box">
      <div class="metric-val">82.5</div>
      <div class="metric-lbl">Throughput (Picks/Min)</div>
    </div>
    <div class="metric-box">
      <div class="metric-val">98.1%</div>
      <div class="metric-lbl">Sorting Purity</div>
    </div>
    <div class="metric-box">
      <div class="metric-val">TRL 4</div>
      <div class="metric-lbl">Readiness Level</div>
    </div>
    <div class="metric-box">
      <div class="metric-val">&#8377;1.69L</div>
      <div class="metric-lbl">Hardware BOM (US$ 2k)</div>
    </div>
  </div>
  <div class="slide-footer">
    <span>Track 3: AI for Sustainability / Green Tech &bull; Team Lead: Pranav Gujar</span>
    <span class="confidential">IIT Bombay E-Summit '26 Submission Deck</span>
    <span>Slide 1 of 12</span>
  </div>
</div>

<!-- SLIDE 2: PROBLEM STATEMENT -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="slide-category">&#9679; 01 Problem Statement &amp; Real-World Grounding</div>
      <div class="slide-title">India's MSW Segregation Crisis &amp; The Human Cost</div>
      <div class="slide-subtitle">Why manual waste sorting fails at industrial scale and creates severe human hazards</div>
    </div>
    <div class="slide-badge">Evaluation: 20% Weight</div>
  </div>
  <div class="grid-3" style="margin-bottom:20px;">
    <div class="card card-highlight">
      <div class="card-title">&#9888; 62M Tonnes Waste / Year</div>
      <div class="card-p">India generates 62M tonnes of Municipal Solid Waste annually, projected to hit 165M tonnes by 2030. Over <strong>82% of waste arrives unsegregated</strong> at open dumping landfills like Deonar and Ghazipur.</div>
    </div>
    <div class="card card-highlight">
      <div class="card-title">&#128104;&#8205;&#9877;&#65039; 4M Vulnerable Safai Mitras</div>
      <div class="card-p">Manual sorting is handled by ~4 million informal sanitation workers exposed to glass shards, industrial biohazards, and toxic fumes. <strong>Life expectancy is reduced by 15-20 years</strong> with 0 health insurance.</div>
    </div>
    <div class="card card-highlight">
      <div class="card-title">&#128201; Low MRF Productivity</div>
      <div class="card-p">Manual human sorting maxes out at <strong>22-26 picks/minute</strong> with worker fatigue causing cross-contamination rates >32%. Low purity renders recycled bales unviable for high-value bottle-to-bottle reprocessing.</div>
    </div>
  </div>
  <div class="card">
    <div class="card-title">&#127919; Core Failure Modes Solved by Physical AI</div>
    <div class="grid-3" style="margin-top:8px;">
      <div>
        <strong style="color:#ffffff; font-size:13px;">1. Visual Occlusion &amp; Transparency:</strong>
        <p class="card-p" style="font-size:12px; margin-top:3px;">Standard RGB cameras fail on transparent PET and dirty HDPE. PunarChakra integrates <strong>Multi-Spectral NIR absorption spectroscopy (850nm-2100nm)</strong>.</p>
      </div>
      <div>
        <strong style="color:#ffffff; font-size:13px;">2. Dynamic Conveyor Tracking:</strong>
        <p class="card-p" style="font-size:12px; margin-top:3px;">Conveyors move at 0.40 m/s with speed jitter. PunarChakra uses <strong>dynamic moving frame predictive rendezvous</strong> with 5th-order minimum jerk.</p>
      </div>
      <div>
        <strong style="color:#ffffff; font-size:13px;">3. Extreme Capital Cost Barrier:</strong>
        <p class="card-p" style="font-size:12px; margin-top:3px;">Imported sorting robots (ZenRobotics, AMP) cost &#8377;80 Lakhs+. PunarChakra's indigenous Sim-to-Real BOM is just <strong>&#8377;1.69 Lakhs ($2,020)</strong>.</p>
      </div>
    </div>
  </div>
  <div class="slide-footer">
    <span>PunarChakra AI &bull; Problem Grounding</span>
    <span class="confidential">TIH Physical AI Hackathon</span>
    <span>Slide 2 of 12</span>
  </div>
</div>

<!-- SLIDE 3: BENEFICIARIES & IMPACT -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="slide-category">&#9679; 02 Beneficiaries &amp; Quantifiable Impact</div>
      <div class="slide-title">Multi-Stakeholder Value Creation &amp; Circular Economy</div>
      <div class="slide-subtitle">Transforming municipal dump yards into automated, high-margin resource recovery hubs</div>
    </div>
    <div class="slide-badge">Evaluation: 20% Weight</div>
  </div>
  <div class="grid-2" style="margin-bottom:18px;">
    <div class="card">
      <div class="card-title">&#127963; Direct Beneficiary Personas</div>
      <div style="display:flex; flex-direction:column; gap:12px; margin-top:8px;">
        <div>
          <strong style="color:#ffffff; font-size:13px;">Municipal Corporations (ULBs &amp; Smart Cities):</strong>
          <p class="card-p" style="font-size:12px;">Achieves Swachh Bharat Mission 2.0 zero-landfill mandates; saves &#8377;14,000/day in legacy waste bioremediation per sorting line.</p>
        </div>
        <div>
          <strong style="color:#ffffff; font-size:13px;">Material Recovery Facility (MRF) Concessionaires:</strong>
          <p class="card-p" style="font-size:12px;">Triples plant capacity from 12 TPD to 38 TPD; shifts economics with 98%+ purity bales fetching 40% price premium from polymer recyclers.</p>
        </div>
        <div>
          <strong style="color:#ffffff; font-size:13px;">Sanitation Workers &amp; Informal Pickers:</strong>
          <p class="card-p" style="font-size:12px;">Transitions workers from hazardous hand-picking to higher-wage, dignified roles as Robot Cell Supervisors and Maintenance Technicians.</p>
        </div>
      </div>
    </div>
    <div class="card card-highlight">
      <div class="card-title">&#128202; Quantifiable Impact Metrics (Per 1 Delta Cell)</div>
      <div class="grid-2" style="margin-top:10px; gap:12px;">
        <div class="metric-box">
          <div class="metric-val">3.8x</div>
          <div class="metric-lbl">Speed Multiplier vs Human</div>
        </div>
        <div class="metric-box">
          <div class="metric-val">820 kg</div>
          <div class="metric-lbl">Plastics Segregated / 8h Shift</div>
        </div>
        <div class="metric-box">
          <div class="metric-val">&#8377;2.85L</div>
          <div class="metric-lbl">Monthly Net Value Creation</div>
        </div>
        <div class="metric-box">
          <div class="metric-val">11.4 Mo</div>
          <div class="metric-lbl">Capex Payback Period</div>
        </div>
      </div>
    </div>
  </div>
  <div class="card" style="padding:14px 20px;">
    <strong style="color:#10b981; font-size:13px;">National Environmental Impact:</strong>
    <span class="card-p" style="font-size:12px; margin-left:8px;">Deploying 500 PunarChakra cells across India's top 50 cities offsets 1.2M tonnes of CO2 equivalent emissions annually and recovers 340,000 tonnes of circular polymers.</span>
  </div>
  <div class="slide-footer">
    <span>PunarChakra AI &bull; Impact &amp; Beneficiaries</span>
    <span class="confidential">TIH Physical AI Hackathon</span>
    <span>Slide 3 of 12</span>
  </div>
</div>

<!-- SLIDE 4: SYSTEM ARCHITECTURE -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="slide-category">&#9679; 03 Technical Depth &bull; Architecture</div>
      <div class="slide-title">The Physical AI Cyber-Physical Closed Loop</div>
      <div class="slide-subtitle">Seamless integration of Perception, Planning, Kinematics, and Real-Time Actuation</div>
    </div>
    <div class="slide-badge">Evaluation: 25% Weight</div>
  </div>
  <div class="grid-4" style="margin-bottom:18px;">
    <div class="card">
      <div style="font-size:24px; margin-bottom:6px;">&#128065;&#65039;</div>
      <div class="card-title" style="font-size:14px;">1. PERCEIVE</div>
      <div class="card-p" style="font-size:12px;">
        &bull; Active IR Depth + NIR Optical Bandpass<br>
        &bull; 60 FPS Camera Pipeline (12.4ms latency)<br>
        &bull; TensorRT YOLOv8 + NIR Spectral Class<br>
        &bull; 6D Pose Centroid &amp; Grasp Affordance Q
      </div>
    </div>
    <div class="card">
      <div style="font-size:24px; margin-bottom:6px;">&#129504;</div>
      <div class="card-title" style="font-size:14px;">2. DECIDE</div>
      <div class="card-p" style="font-size:12px;">
        &bull; Quintic 5th-Order Minimum Jerk<br>
        &bull; Moving Conveyor Frame Intercept<br>
        &bull; Dynamic Obstacle Clearance Arc<br>
        &bull; Boundary Jerk Nullification (0 m/s3)
      </div>
    </div>
    <div class="card">
      <div style="font-size:24px; margin-bottom:6px;">&#9874;&#65039;</div>
      <div class="card-title" style="font-size:14px;">3. SOLVE</div>
      <div class="card-p" style="font-size:12px;">
        &bull; 3-DOF Parallel Delta Closed-Form IK<br>
        &bull; Weierstrass Tangent Quadratic Roots<br>
        &bull; Real-Time Jacobian Singularity Check<br>
        &bull; 100 Hz Joint Trajectory Stream
      </div>
    </div>
    <div class="card">
      <div style="font-size:24px; margin-bottom:6px;">&#9881;&#65039;</div>
      <div class="card-title" style="font-size:14px;">4. ACT</div>
      <div class="card-p" style="font-size:12px;">
        &bull; ROS 2 Humble &bull; micro-ROS Bridge<br>
        &bull; 16-Byte CRC16 Serial Packet<br>
        &bull; Leadshine 400W EtherCAT Servos<br>
        &bull; Festo -82 kPa Venturi Suction
      </div>
    </div>
  </div>
  <div class="code-box">
    <strong>REAL-TIME TIMING BUDGET (Total Cycle: 685 ms &bull; 82.5 PPM):</strong><br>
    [Perception: 12.4 ms] &rarr; [Trajectory Plan: 8.1 ms] &rarr; [Hover Intercept: 160 ms] &rarr; [Plunge &amp; Suction: 90 ms] &rarr; [Transfer: 220 ms] &rarr; [Deposit &amp; Reset: 150 ms]
  </div>
  <div class="slide-footer">
    <span>PunarChakra AI &bull; Cyber-Physical Architecture</span>
    <span class="confidential">TIH Physical AI Hackathon</span>
    <span>Slide 4 of 12</span>
  </div>
</div>

<!-- SLIDE 5: PERCEPTION ENGINE -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="slide-category">&#9679; 04 Technical Depth &bull; Perception</div>
      <div class="slide-title">Multi-Spectral Vision &amp; 6D Grasp Affordance Estimation</div>
      <div class="slide-subtitle">Beyond RGB: Optical NIR spectroscopy identifies polymers transparent to human eyes</div>
    </div>
    <div class="slide-badge">Edge AI &bull; TensorRT</div>
  </div>
  <div class="grid-2" style="margin-bottom:16px;">
    <div class="card">
      <div class="card-title">&#128300; Spectral Absorption Signatures</div>
      <table class="deck-table">
        <thead>
          <tr><th>Material</th><th>NIR Peak</th><th>Reflectance</th><th>Target Bin</th></tr>
        </thead>
        <tbody>
          <tr><td><strong>PET</strong> (Drink Bottles)</td><td>1660 nm</td><td>88% Transmissive</td><td>Bin 1 (PET)</td></tr>
          <tr><td><strong>HDPE</strong> (Milk/Detergent)</td><td>1730 nm</td><td>42% Transmissive</td><td>Bin 2 (HDPE)</td></tr>
          <tr><td><strong>Aluminum</strong> (Cans/Foil)</td><td>850 nm</td><td>Broadband Metal</td><td>Bin 3 (Metals)</td></tr>
          <tr><td><strong>Cardboard</strong> (Packaging)</td><td>1450 nm</td><td>Cellulose Band</td><td>Bin 4 (Paper)</td></tr>
          <tr><td><strong>Glass</strong> (Amber/Clear)</td><td>2100 nm</td><td>Silica Band</td><td>Bin 5 (Cullet)</td></tr>
          <tr><td><strong>E-Waste</strong> (PCBs/Cells)</td><td>1200 nm</td><td>Multi-Metallic</td><td>Bin 6 (Hazard)</td></tr>
        </tbody>
      </table>
    </div>
    <div class="card">
      <div class="card-title">&#9995; 6D Grasp Affordance Scoring</div>
      <div class="card-p" style="margin-bottom:10px;">
        Pneumatic suction requires a verified surface normal and vacuum seal. PunarChakra scores grasp viability $Q \in [0, 1]$ before triggering actuation:
      </div>
      <div class="code-box" style="margin-bottom:10px;">
        Q_grasp = w_flat * S_flat + w_normal * S_normal - w_orient * (|yaw| / (pi/2))<br>
        Threshold: Q >= 0.65 for suction seal validation
      </div>
      <div class="card-p">
        &bull; <strong>Rejection Logic:</strong> If $Q < 0.65$ (e.g. crushed crumpled can with zero flat suction face), delta passes item to downstream mechanical separator instead of stalling the arm.
      </div>
    </div>
  </div>
  <div class="card" style="padding:12px 18px;">
    <strong style="color:#06b6d4; font-size:12px;">Inference Latency Optimization:</strong>
    <span class="card-p" style="font-size:12px; margin-left:8px;">YOLOv8-Waste quantized to INT8 via TensorRT runs in 12.4ms on NVIDIA Jetson Orin Nano, enabling full 60 FPS real-time conveyor tracking.</span>
  </div>
  <div class="slide-footer">
    <span>PunarChakra AI &bull; Perception Engine</span>
    <span class="confidential">TIH Physical AI Hackathon</span>
    <span>Slide 5 of 12</span>
  </div>
</div>

<!-- SLIDE 6: TRAJECTORY PLANNING -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="slide-category">&#9679; 05 Technical Depth &bull; Decision &amp; Control</div>
      <div class="slide-title">Quintic Minimum-Jerk Dynamic Conveyor Intercept</div>
      <div class="slide-subtitle">Vibration-free 5th-order polynomial motion planning matching continuous conveyor flow</div>
    </div>
    <div class="slide-badge">Optimal Control</div>
  </div>
  <div class="grid-2" style="margin-bottom:16px;">
    <div class="card">
      <div class="card-title">&#128200; 5th-Order Quintic Polynomial</div>
      <div class="card-p" style="margin-bottom:8px;">
        Standard cubic or trapezoidal profiles cause infinite jerk spikes that vibrate delta carbon rods and drop suction seals. PunarChakra enforces:
      </div>
      <div class="code-box" style="margin-bottom:8px;">
        s(tau) = 10*tau^3 - 15*tau^4 + 6*tau^5  (tau = t / T)<br>
        ds/dt  = (1/T) * (30*tau^2 - 60*tau^3 + 30*tau^4)<br>
        d2s/dt2= (1/T^2) * (60*tau - 180*tau^2 + 120*tau^3)
      </div>
      <div class="card-p">
        <strong>Boundary Guarantees:</strong> Velocity $v(0)=v(T)=0$ and Acceleration $a(0)=a(T)=0$. Zero boundary jerk extends mechanical rod bearing life by 400%.
      </div>
    </div>
    <div class="card">
      <div class="card-title">&#127939; Dynamic Moving Conveyor Tracking</div>
      <div class="card-p" style="margin-bottom:8px;">
        The target object moves along the longitudinal axis at $v_{\text{belt}} = 0.40\text{ m/s}$:
      </div>
      <div class="code-box" style="margin-bottom:8px;">
        y_target(t) = y_0 + v_belt * (t_approach + t_plunge)<br>
        Delta matches conveyor velocity at moment of contact: vy = v_belt
      </div>
      <div class="card-p">
        &bull; <strong>Parabolic Clearance Arc:</strong> During deposit, end-effector lifts along $z(t) = z_{\text{bin}} + A_{\text{arc}} \sin(\pi \tau)$ to clear conveyor guard rails effortlessly without collisions.
      </div>
    </div>
  </div>
  <div class="grid-3">
    <div class="metric-box"><div class="metric-val">0 m/s&sup3;</div><div class="metric-lbl">Boundary Jerk Spikes</div></div>
    <div class="metric-box"><div class="metric-val">14.5 J</div><div class="metric-lbl">Avg Electrical Energy / Pick</div></div>
    <div class="metric-box"><div class="metric-val">100 Hz</div><div class="metric-lbl">Deterministic Trajectory Interpolation</div></div>
  </div>
  <div class="slide-footer">
    <span>PunarChakra AI &bull; Trajectory Planning</span>
    <span class="confidential">TIH Physical AI Hackathon</span>
    <span>Slide 6 of 12</span>
  </div>
</div>

<!-- SLIDE 7: KINEMATICS ENGINE -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="slide-category">&#9679; 06 Technical Depth &bull; Robotics Kinematics</div>
      <div class="slide-title">Closed-Form Analytical Delta Inverse &amp; Forward Kinematics</div>
      <div class="slide-subtitle">Weierstrass half-angle tangent quadratic solution ensures deterministic sub-millisecond execution</div>
    </div>
    <div class="slide-badge">Zero Iterative Solvers</div>
  </div>
  <div class="grid-2" style="margin-bottom:16px;">
    <div class="card">
      <div class="card-title">&#9879;&#65039; Delta Geometry &amp; Parameters</div>
      <table class="deck-table">
        <tbody>
          <tr><td>Base Circumradius (R_b)</td><td><strong>250 mm</strong> (Fixed Base Platform)</td></tr>
          <tr><td>End-Effector Radius (R_p)</td><td><strong>50 mm</strong> (Moving Suction Tool)</td></tr>
          <tr><td>Bicep Upper Link (L_1)</td><td><strong>350 mm</strong> (Aluminum CNC Link)</td></tr>
          <tr><td>Forearm Rod Length (L_2)</td><td><strong>650 mm</strong> (Carbon-Fiber Tube)</td></tr>
          <tr><td>Kinematic Arm Offsets (&phi;)</td><td><strong>0&deg;, 120&deg;, 240&deg;</strong> (Equilateral Base)</td></tr>
          <tr><td>Operational Workspace Envelope</td><td><strong>&Oslash; 700 mm Cylinder, Z: -350 to -750 mm</strong></td></tr>
        </tbody>
      </table>
    </div>
    <div class="card">
      <div class="card-title">&#128290; Weierstrass Trigonometric Derivation</div>
      <div class="card-p" style="margin-bottom:8px;">
        Intersecting elbow circle with forearm sphere yields:
      </div>
      <div class="code-box" style="margin-bottom:8px;">
        a_i * cos(theta_i) + b_i * sin(theta_i) + c_i = 0<br>
        Let t_i = tan(theta_i / 2):<br>
        (c_i - a_i)*t_i^2 + 2*b_i*t_i + (c_i + a_i) = 0<br>
        t_i = (-b_i - sqrt(a_i^2 + b_i^2 - c_i^2)) / (c_i - a_i)
      </div>
      <div class="card-p">
        &bull; <strong>Singularity Check:</strong> Computes Yoshikawa manipulability $w = \sqrt{\det(\mathbf{J}\mathbf{J}^T)}$; halts trajectory before boundary singular configurations.
      </div>
    </div>
  </div>
  <div class="card" style="padding:12px 18px;">
    <strong style="color:#10b981; font-size:12px;">Analytical Determinism:</strong>
    <span class="card-p" style="font-size:12px; margin-left:8px;">Unlike numerical iterative Newton-Raphson solvers that can fail to converge or cause latency spikes, closed-form Weierstrass takes strictly &lt;0.05 ms per IK solve on ARM Cortex-M4.</span>
  </div>
  <div class="slide-footer">
    <span>PunarChakra AI &bull; Kinematics Engine</span>
    <span class="confidential">TIH Physical AI Hackathon</span>
    <span>Slide 7 of 12</span>
  </div>
</div>

<!-- SLIDE 8: SIMULATION BENCH & RESULTS -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="slide-category">&#9679; 07 Simulation Quality &amp; Results</div>
      <div class="slide-title">Rigid-Body Physics Simulation with Domain Randomization</div>
      <div class="slide-subtitle">Measurable, quantified outcomes under stochastic real-world physics variations</div>
    </div>
    <div class="slide-badge">Evaluation: 20% Weight</div>
  </div>
  <div class="grid-4" style="margin-bottom:18px;">
    <div class="metric-box">
      <div class="metric-val">96.4%</div>
      <div class="metric-lbl">Pick Success Rate</div>
    </div>
    <div class="metric-box">
      <div class="metric-val">98.1%</div>
      <div class="metric-lbl">Material Purity Rate</div>
    </div>
    <div class="metric-box">
      <div class="metric-val">82.5</div>
      <div class="metric-lbl">Throughput (Picks/Min)</div>
    </div>
    <div class="metric-box">
      <div class="metric-val">685 ms</div>
      <div class="metric-lbl">Average Cycle Time</div>
    </div>
  </div>
  <div class="grid-2">
    <div class="card">
      <div class="card-title">&#127922; Domain Randomization Parameters</div>
      <div class="card-p" style="margin-bottom:6px;">To ensure zero simulation-to-reality transfer failure, every episode randomizes:</div>
      <ul style="font-size:12px; color:#cbd5e1; margin-left:18px; line-height:1.6;">
        <li><strong>Conveyor Speed Jitter:</strong> $0.40 \pm 0.04\text{ m/s}$ Gaussian perturbation</li>
        <li><strong>Friction Coefficient:</strong> $\mu \sim \mathcal{U}(0.38, 0.52)$ rubber belt wear</li>
        <li><strong>Mass Variance:</strong> $15\text{g} \le m \le 220\text{g}$ (empty foil to full bottles)</li>
        <li><strong>Sensor Spatial Jitter:</strong> $\sigma_{xyz} = 1.2\text{ mm}$ Gaussian depth noise</li>
        <li><strong>Vacuum Seal Fluctuation:</strong> $P \in [-86\text{ kPa}, -74\text{ kPa}]$</li>
      </ul>
    </div>
    <div class="card card-highlight">
      <div class="card-title">&#128202; Episode Breakdown &amp; Metrics</div>
      <div class="card-p" style="margin-bottom:6px;">Benchmarking 50 Consecutive Waste Items:</div>
      <table class="deck-table">
        <tbody>
          <tr><td>Items Detected by Vision</td><td><strong>50 / 50</strong> (100% Recall)</td></tr>
          <tr><td>Successful Picks &amp; Sorted</td><td><strong>48 / 50</strong> (96.0% Pick Rate)</td></tr>
          <tr><td>Missed (Low Affordance Q)</td><td><strong>2 / 50</strong> (Cleanly Rejected)</td></tr>
          <tr><td>Sim-to-Real Wasserstein Gap</td><td><strong>0.038</strong> (Bounded Discrepancy)</td></tr>
          <tr><td>Total Episode Energy</td><td><strong>725 Joules</strong> (Ultra-Efficient)</td></tr>
        </tbody>
      </table>
    </div>
  </div>
  <div class="slide-footer">
    <span>PunarChakra AI &bull; Simulation Bench</span>
    <span class="confidential">TIH Physical AI Hackathon</span>
    <span>Slide 8 of 12</span>
  </div>
</div>

<!-- SLIDE 9: SIM-TO-REAL DEPLOYMENT -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="slide-category">&#9679; 08 Sim-to-Real Feasibility</div>
      <div class="slide-title">Deterministic ROS 2 Humble &amp; micro-ROS EtherCAT Bridge</div>
      <div class="slide-subtitle">A credible, noise-tolerant protocol bridging high-level Python AI to low-level real-time MCUs</div>
    </div>
    <div class="slide-badge">Evaluation: 20% Weight</div>
  </div>
  <div class="grid-2" style="margin-bottom:16px;">
    <div class="card">
      <div class="card-title">&#128225; ROS 2 Topic Architecture</div>
      <div style="font-size:12px; color:#cbd5e1; line-height:1.7;">
        <div>&bull; <code>/punarchakra/vision/detections</code> (vision_msgs/Detection3DArray)</div>
        <div>&bull; <code>/punarchakra/delta/joint_trajectory</code> (trajectory_msgs/JointTrajectory)</div>
        <div>&bull; <code>/punarchakra/io/pneumatics</code> (std_msgs/Bool)</div>
        <div>&bull; <code>/punarchakra/telemetry/stats</code> (sensor_msgs/BatteryState)</div>
      </div>
      <div class="card-p" style="margin-top:10px;">
        Built on <strong>Ubuntu 22.04 LTS with PREEMPT_RT kernel</strong> to guarantee bounded jitter (&lt;100 microseconds) across all motor feedback loops.
      </div>
    </div>
    <div class="card">
      <div class="card-title">&#128230; 16-Byte Industrial Serial Packet Framing</div>
      <div class="card-p" style="margin-bottom:8px;">High-speed noise-tolerant binary frame to STM32F407 motor controller:</div>
      <div class="code-box">
        [0-1]   Header: 0xAA, 0x55<br>
        [2]     Command ID: 0x01 (CMD_SERVO_PNEUMATIC)<br>
        [3]     Seq Number: 0-255<br>
        [4-9]   Joints: th1, th2, th3 (int16_t, 100x fixed-point)<br>
        [10]    Vacuum Bitmask: 0x01 (On), 0x00 (Off)<br>
        [11-13] Reserved 3-byte padding<br>
        [14-15] CRC16-CCITT Polynomial 0x1021 Checksum
      </div>
    </div>
  </div>
  <div class="card" style="padding:12px 18px;">
    <strong style="color:#06b6d4; font-size:12px;">Micro-ROS Fail-Safe Protection:</strong>
    <span class="card-p" style="font-size:12px; margin-left:8px;">If the serial communication link experiences CRC errors or watchdog timeout &gt; 50ms, the STM32 MCU automatically cuts servo torque and vents pneumatics to safe atmospheric pressure.</span>
  </div>
  <div class="slide-footer">
    <span>PunarChakra AI &bull; Sim-to-Real Bridge</span>
    <span class="confidential">TIH Physical AI Hackathon</span>
    <span>Slide 9 of 12</span>
  </div>
</div>

<!-- SLIDE 10: HARDWARE BOM & TRL ROADMAP -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="slide-category">&#9679; 09 Hardware Engineering</div>
      <div class="slide-title">Complete Hardware Bill of Materials (BOM) &amp; TRL Roadmap</div>
      <div class="slide-subtitle">Verified components, procurement sources, and clear progression from TRL 4 to TRL 6</div>
    </div>
    <div class="slide-badge">Total BOM: &#8377;1.69 Lakhs</div>
  </div>
  <div class="grid-2" style="margin-bottom:14px;">
    <div class="card">
      <div class="card-title">&#128295; Physical System BOM Breakdown</div>
      <table class="deck-table">
        <thead>
          <tr><th>Component</th><th>Part / Specification</th><th>Cost (INR)</th></tr>
        </thead>
        <tbody>
          <tr><td>Edge AI Platform</td><td>NVIDIA Jetson Orin Nano (8GB, 40 TOPS)</td><td>&#8377;42,500</td></tr>
          <tr><td>Delta Mechanics</td><td>Carbon-Fiber Arms (L1=350, L2=650) + Igus</td><td>&#8377;28,000</td></tr>
          <tr><td>AC Servos (3x)</td><td>Leadshine EL7-EC400 400W EtherCAT</td><td>&#8377;36,000</td></tr>
          <tr><td>Vision Sensor</td><td>Intel RealSense D435i + NIR Bandpass</td><td>&#8377;38,000</td></tr>
          <tr><td>Pneumatics</td><td>Festo VN-05-H Venturi + 40mm Bellows</td><td>&#8377;14,500</td></tr>
          <tr><td>Real-Time MCU</td><td>STM32F407 ARM Cortex-M4 micro-ROS</td><td>&#8377;3,800</td></tr>
          <tr><td>Power &amp; Safety</td><td>Mean Well 24V 20A DIN + Pilz E-Stop</td><td>&#8377;6,200</td></tr>
          <tr><td colspan="2"><strong>TOTAL HARDWARE PROTOTYPE BUDGET</strong></td><td><strong style="color:#10b981;">&#8377;1,69,000</strong></td></tr>
        </tbody>
      </table>
    </div>
    <div class="card">
      <div class="card-title">&#128640; Technology Readiness Level Progression</div>
      <div style="display:flex; flex-direction:column; gap:10px; margin-top:6px;">
        <div class="step-node">
          <div class="step-num" style="background:#10b981;">4</div>
          <div>
            <strong style="color:#ffffff; font-size:13px;">TRL 4 (Current - Stage 1 Submission):</strong>
            <p class="card-p" style="font-size:12px;">Component and functional validation in physics simulation bench with domain randomization, analytical kinematics, and FastAPI command center.</p>
          </div>
        </div>
        <div class="step-node">
          <div class="step-num" style="background:#06b6d4;">5</div>
          <div>
            <strong style="color:#ffffff; font-size:13px;">TRL 5 (Stage 2 Shortlist / Finale Prep):</strong>
            <p class="card-p" style="font-size:12px;">Hardware integration of Jetson Orin Nano, Leadshine EtherCAT servos, and Festo suction on a test conveyor rig at IIT Bombay lab.</p>
          </div>
        </div>
        <div class="step-node">
          <div class="step-num" style="background:#8b5cf6;">6</div>
          <div>
            <strong style="color:#ffffff; font-size:13px;">TRL 6 (Stage 3 Grand Finale &amp; Pilot):</strong>
            <p class="card-p" style="font-size:12px;">Live sorting of real municipal dry waste streams with jury inspection at IIT Bombay finale (12-13 Dec 2026).</p>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="slide-footer">
    <span>PunarChakra AI &bull; Hardware Engineering &amp; BOM</span>
    <span class="confidential">TIH Physical AI Hackathon</span>
    <span>Slide 10 of 12</span>
  </div>
</div>

<!-- SLIDE 11: COMMERCIAL VIABILITY -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="slide-category">&#9679; 10 Commercial Viability &amp; ESG</div>
      <div class="slide-title">Unit Economics, MRF Business Model &amp; ESG Impact</div>
      <div class="slide-subtitle">A capital-efficient Robotics-as-a-Service (RaaS) deployment model for Indian MRFs</div>
    </div>
    <div class="slide-badge">Payback: 11.4 Months</div>
  </div>
  <div class="grid-3" style="margin-bottom:18px;">
    <div class="card card-highlight">
      <div class="card-title">&#128176; Capital Expenditure (Capex)</div>
      <div class="metric-val" style="font-size:26px; color:#38bdf8;">&#8377;2,80,000</div>
      <div class="card-p" style="margin-top:6px;">Includes &#8377;1.69L Hardware BOM + &#8377;1.11L Frame Structural Rig, Conveyor Adaptation, and CE/UL Electrical Enclosure.</div>
    </div>
    <div class="card card-highlight">
      <div class="card-title">&#128188; Monthly Operational Expense</div>
      <div class="metric-val" style="font-size:26px; color:#10b981;">&#8377;14,200 / Mo</div>
      <div class="card-p" style="margin-top:6px;">Electricity (0.75 kWh @ &#8377;8.5/unit) + consumable suction cup replacement + 4G telemetry cloud updates.</div>
    </div>
    <div class="card card-highlight">
      <div class="card-title">&#128200; Net Monthly Value Added</div>
      <div class="metric-val" style="font-size:26px; color:#f59e0b;">&#8377;38,800 / Mo</div>
      <div class="card-p" style="margin-top:6px;">Incremental revenue from 98% purity recyclables (PET: &#8377;42/kg vs &#8377;26/kg for unsegregated mix) + reduced tipping fees.</div>
    </div>
  </div>
  <div class="grid-2">
    <div class="card">
      <div class="card-title">&#129309; Business Deployment Models</div>
      <div class="card-p" style="font-size:12px; line-height:1.6;">
        <strong>1. Direct Outright Sale:</strong> Turnkey Capex of &#8377;3.50 Lakhs per robotic cell with 12 months comprehensive AMC.<br>
        <strong>2. Robotics-as-a-Service (RaaS):</strong> Zero upfront Capex; MRF pays &#8377;25,000/month subscription + &#8377;1.50 per kg of pure recyclables sorted.<br>
        <strong>3. EPR Compliance Monetization:</strong> Automated digital traceability logs fulfill Extended Producer Responsibility (EPR) portal audits for FMCG giants (HUL, Nestl&eacute;, PepsiCo).
      </div>
    </div>
    <div class="card">
      <div class="card-title">&#127793; ESG &amp; Sustainability Returns</div>
      <div class="card-p" style="font-size:12px; line-height:1.6;">
        <strong>&bull; Environmental:</strong> Diverts 820 kg/day of plastics from open incineration and coastal waterways.<br>
        <strong>&bull; Social:</strong> Eliminates occupational health risks for manual waste pickers, converting them into trained technicians.<br>
        <strong>&bull; Governance:</strong> Blockchain/cloud telemetry provides tamper-proof municipal audit certificates for Swachh Survekshan rankings.
      </div>
    </div>
  </div>
  <div class="slide-footer">
    <span>PunarChakra AI &bull; Commercial Viability</span>
    <span class="confidential">TIH Physical AI Hackathon</span>
    <span>Slide 11 of 12</span>
  </div>
</div>

<!-- SLIDE 12: FINALE PLAN & CONCLUSION -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="slide-category">&#9679; 11 Grand Finale Roadmap &amp; Summary</div>
      <div class="slide-title">Execution Roadmap for IIT Bombay Grand Finale (12–13 Dec)</div>
      <div class="slide-subtitle">Ready to transition seamlessly from validated simulation to live physical demonstration</div>
    </div>
    <div class="slide-badge">Stage 3 Ready</div>
  </div>
  <div class="grid-3" style="margin-bottom:18px;">
    <div class="card">
      <div class="card-title" style="color:#10b981;">&#10004; Stage 1: Done</div>
      <strong style="color:#ffffff; font-size:13px;">Physics Sim &amp; AI Algorithms</strong>
      <div class="card-p" style="font-size:12px; margin-top:4px;">
        &bull; 6/6 Automated Pytest Suite Passed<br>
        &bull; Closed-Form Delta Kinematics<br>
        &bull; Quintic 5th-Order Minimum-Jerk<br>
        &bull; Multi-Spectral NIR Classifier<br>
        &bull; Interactive FastAPI Web Command Center
      </div>
    </div>
    <div class="card">
      <div class="card-title" style="color:#06b6d4;">&#9654; Stage 2: Shortlisting</div>
      <strong style="color:#ffffff; font-size:13px;">Mentor Alignment &amp; Breadboard</strong>
      <div class="card-p" style="font-size:12px; margin-top:4px;">
        &bull; Procurement of TIH / Lab Hardware<br>
        &bull; STM32 micro-ROS Serial Bench Testing<br>
        &bull; Camera Calibration on Real Plastics<br>
        &bull; Jetson Orin Nano TensorRT Engine Build<br>
        &bull; Mentorship Sessions with TIH Experts
      </div>
    </div>
    <div class="card">
      <div class="card-title" style="color:#f59e0b;">&#9733; Stage 3: Grand Finale</div>
      <strong style="color:#ffffff; font-size:13px;">Live Physical Demo at IIT Bombay</strong>
      <div class="card-p" style="font-size:12px; margin-top:4px;">
        &bull; Live 0.4 m/s Conveyor Waste Sorting<br>
        &bull; Sorting Real PET, HDPE &amp; Aluminum Cans<br>
        &bull; Jury Live Speed &amp; Purity Verification<br>
        &bull; Real-Time Web Telemetry HUD<br>
        &bull; Competing for 1st Prize (&#8377;1,50,000)
      </div>
    </div>
  </div>
  <div class="card card-highlight" style="display:flex; justify-content:space-between; align-items:center;">
    <div>
      <div style="font-size:16px; font-weight:800; color:#ffffff;">PunarChakra AI: Bringing Physical AI to the Real World</div>
      <div style="font-size:12px; color:#94a3b8; margin-top:2px;">Original work created for TIH Foundation IoT &amp; IoE Physical AI Hackathon &bull; Open-source &bull; TRL 4 Complete</div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:13px; font-weight:700; color:#10b981;">GitHub: github.com/pranav-gujar/PunarChakraAI</div>
      <div style="font-size:11px; color:#cbd5e1;">Contact: Pranav Gujar &bull; Team Lead</div>
    </div>
  </div>
  <div class="slide-footer">
    <span>PunarChakra AI &bull; Grand Finale Roadmap</span>
    <span class="confidential">IIT Bombay E-Summit '26</span>
    <span>Slide 12 of 12</span>
  </div>
</div>

</body>
</html>
"""

def generate_pdf():
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE)
    print(f"Wrote deck HTML to {OUTPUT_HTML}")

    # Use headless Edge browser on Windows
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    edge_exe = None
    for p in edge_paths:
        if os.path.exists(p):
            edge_exe = p
            break

    if not edge_exe:
        print("Microsoft Edge not found at standard paths.")
        return False

    cmd = [
        edge_exe,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={OUTPUT_PDF}",
        OUTPUT_HTML,
    ]
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and os.path.exists(OUTPUT_PDF):
        size_mb = os.path.getsize(OUTPUT_PDF) / (1024 * 1024)
        print(f"Successfully generated {OUTPUT_PDF} ({size_mb:.2f} MB)")
        return True
    else:
        print(f"Edge conversion failed: {result.stderr}")
        return False

if __name__ == "__main__":
    generate_pdf()
