import json
import math
import random
from pathlib import Path
from typing import Callable, Dict, Any

def run_robotics_simulation(
    candidate_controller: Callable[[float, float, float, float], float],
    perturbation_file: Path,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Runs a deterministic 10-second physical arm stabilization test with mid-run adversarial failures.
    candidate_controller(target_rad, measured_angle_rad, angular_vel_rad_s, dt) -> torque_command_nm
    """
    random.seed(seed)
    spec = json.loads(perturbation_file.read_text())
    
    target = spec["target_angle_rad"]
    dt = spec["dt_sec"]
    steps = int(spec["simulation_duration_sec"] / dt)
    perturbations = spec["perturbations"]

    # Initial physical state of the robotic joint
    angle = 0.0
    vel = 0.0
    mass = 1.5          # kg
    length = 0.6        # meters
    gravity = 9.81
    damping = 0.35
    noise_std = 0.002
    max_torque = 35.0   # Nm

    total_abs_error = 0.0
    total_energy_effort = 0.0
    recovery_times = []
    active_perturbation_start = None
    in_recovery = False

    for step in range(steps):
        t = round(step * dt, 3)

        # 1. Inject Adversarial Perturbations at exact timestamps
        for p in perturbations:
            if abs(t - p["trigger_time_sec"]) < (dt / 2.0):
                if p["type"] == "mass_multiplier":
                    mass *= p["value"]
                elif p["type"] == "sensor_noise_std":
                    noise_std = p["value"]
                elif p["type"] == "max_torque_limit_nm":
                    max_torque = p["value"]
                active_perturbation_start = t
                in_recovery = True

        # 2. Sensor reading with noise
        measured_angle = angle + random.gauss(0.0, noise_std)

        # 3. Query candidate's controller for motor torque command
        raw_torque = candidate_controller(target, measured_angle, vel, dt)
        applied_torque = max(-max_torque, min(max_torque, float(raw_torque)))

        # 4. Rigid-body physics integration (I * alpha = tau - m*g*L*sin(theta) - b*vel)
        inertia = mass * (length ** 2)
        gravity_torque = mass * gravity * length * math.sin(angle)
        angular_accel = (applied_torque - gravity_torque - damping * vel) / inertia

        vel += angular_accel * dt
        angle += vel * dt

        # 5. Telemetry tracking
        err = abs(target - angle)
        total_abs_error += err * dt
        total_energy_effort += abs(applied_torque * vel) * dt

        # Measure how fast candidate re-stabilizes within 0.03 rad (~1.7 deg) after a shock
        if in_recovery and err < 0.03 and abs(vel) < 0.05:
            recovery_times.append(round(t - active_perturbation_start, 3))
            in_recovery = False

    # 6. Deterministic Ground-Truth Scoring (0.0 to 1.0)
    accuracy_score = max(0.0, 1.0 - (total_abs_error / 4.0))
    efficiency_score = max(0.0, 1.0 - (total_energy_effort / 250.0))
    
    # Penalize if controller never recovered from any shock
    if len(recovery_times) == len(perturbations):
        avg_recovery = sum(recovery_times) / len(recovery_times)
        recovery_score = max(0.0, 1.0 - (avg_recovery / 2.5))
    else:
        recovery_score = 0.0

    composite_score = round((0.45 * accuracy_score) + (0.35 * recovery_score) + (0.20 * efficiency_score), 4)

    return {
        "cartridge_id": spec["cartridge_id"],
        "composite_score": composite_score,
        "universal_traits": {
            "perturbation_recovery_pct": round(recovery_score * 100, 2),
            "first_principles_efficiency": round(efficiency_score * 100, 2)
        },
        "telemetry": {
            "final_angle_error_rad": round(abs(target - angle), 4),
            "perturbation_recovery_times_sec": recovery_times,
            "total_energy_joules": round(total_energy_effort, 2)
        }
    }

# --- Reference Baseline Test (Naive PID Controller without Anti-Windup or Gravity Feedforward) ---
if __name__ == "__main__":
    integral = 0.0
    def naive_pid(target: float, measured: float, vel: float, dt: float) -> float:
        global integral
        err = target - measured
        integral += err * dt
        return (18.0 * err) + (6.0 * integral) - (3.5 * vel)

    result = run_robotics_simulation(naive_pid, Path(__file__).parent / "perturbations.json")
    print(json.dumps(result, indent=2))
