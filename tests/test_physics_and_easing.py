import math
import pytest
from videomascot.core.math_2d import CubicBezier, SPRING_OVERSHOOT, ANTICIPATION, EASE_OUT_EXPO
from videomascot.animation.procedural import SpringDamper1D, BoneSpringSimulator
from videomascot.models.pose import PoseState
from videomascot.models.manifest import MascotManifest, BoneConfig, PhysicsConfig


def test_cubic_bezier_boundary_and_monotonicity():
    curve = CubicBezier(0.25, 0.1, 0.25, 1.0)
    assert curve.evaluate(0.0) == pytest.approx(0.0, abs=1e-4)
    assert curve.evaluate(1.0) == pytest.approx(1.0, abs=1e-4)

    # Monotonic progression in middle
    mid = curve.evaluate(0.5)
    assert 0.0 < mid < 1.0


def test_cubic_bezier_overshoot():
    # SPRING_OVERSHOOT reaches peak > 1.0 before settling to 1.0
    values = [SPRING_OVERSHOOT.evaluate(t / 100.0) for t in range(101)]
    max_val = max(values)
    assert max_val > 1.02  # Tangible overshoot
    assert values[0] == pytest.approx(0.0, abs=1e-3)
    assert values[-1] == pytest.approx(1.0, abs=1e-3)


def test_cubic_bezier_anticipation():
    # ANTICIPATION dips slightly below 0.0 before accelerating
    values = [ANTICIPATION.evaluate(t / 100.0) for t in range(50)]
    min_val = min(values)
    assert min_val < -0.01  # Tangible anticipation wind-up dip


def test_spring_damper_1d_convergence_and_oscillation():
    # Spring with target = 10.0, starting at 0.0
    spring = SpringDamper1D(stiffness=150.0, damping=12.0, mass=1.0)
    dt = 1.0 / 60.0  # 60 fps step

    positions = []
    for _ in range(120):  # 2 seconds
        pos = spring.update(target=10.0, dt=dt)
        positions.append(pos)

    # Should overshoot slightly because damping ratio zeta = 12 / (2 * sqrt(150)) = 0.489 (underdamped)
    max_pos = max(positions)
    assert max_pos > 10.05
    # Should settle near target by end
    assert positions[-1] == pytest.approx(10.0, abs=0.1)


def test_bone_spring_simulator_with_manifest():
    manifest = MascotManifest(
        id="spring_bot",
        name="Spring Bot",
        bones={
            "root": BoneConfig(position=(0, 0)),
            "torso": BoneConfig(parent="root", position=(0, -100)),
            "antenna": BoneConfig(
                parent="torso",
                position=(0, -50),
                physics=PhysicsConfig(stiffness=180.0, damping=14.0, mass=1.0)
            )
        }
    )

    sim = BoneSpringSimulator(manifest=manifest)
    pose = PoseState()
    
    # Step simulation with sudden torso rotation impulse
    # Antenna should lag and have non-zero secondary rotational offset
    dt = 1.0 / 30.0
    angles = []
    for step in range(30):
        # Sudden jerk on torso for first 5 frames
        torso_rot = 30.0 if step < 5 else 0.0
        pose.set_joint_rotation("torso", torso_rot)
        updated_pose = sim.step(pose, dt=dt)
        angles.append(updated_pose.joint_rotations.get("antenna", 0.0))

    # Antenna must have reacted dynamically (non-zero rotation)
    assert any(abs(a) > 0.5 for a in angles)
