import math
import pytest
import numpy as np
from videomascot.core.math_2d import Vector2D, Transform2D, ease_in_out_quad, ease_out_back, spring_lerp


def test_vector2d_operations():
    v1 = Vector2D(3.0, 4.0)
    v2 = Vector2D(1.0, 2.0)
    
    # Addition & Subtraction
    v_add = v1 + v2
    assert v_add.x == 4.0 and v_add.y == 6.0
    
    v_sub = v1 - v2
    assert v_sub.x == 2.0 and v_sub.y == 2.0
    
    # Scalar multiplication
    v_mul = v1 * 2.0
    assert v_mul.x == 6.0 and v_mul.y == 8.0
    
    # Magnitude & Normalization
    assert pytest.approx(v1.magnitude()) == 5.0
    norm = v1.normalized()
    assert pytest.approx(norm.magnitude()) == 1.0
    assert pytest.approx(norm.x) == 0.6
    assert pytest.approx(norm.y) == 0.8


def test_transform2d_identity():
    t = Transform2D.identity()
    pt = Vector2D(10.0, 20.0)
    transformed = t.transform_point(pt)
    assert pytest.approx(transformed.x) == 10.0
    assert pytest.approx(transformed.y) == 20.0


def test_transform2d_translation():
    t = Transform2D.from_translation(15.0, -5.0)
    pt = Vector2D(10.0, 20.0)
    transformed = t.transform_point(pt)
    assert pytest.approx(transformed.x) == 25.0
    assert pytest.approx(transformed.y) == 15.0


def test_transform2d_rotation_around_origin():
    # 90 degrees clockwise (or standard coordinate rotation)
    t = Transform2D.from_rotation_deg(90.0)
    pt = Vector2D(1.0, 0.0)
    transformed = t.transform_point(pt)
    assert pytest.approx(transformed.x, abs=1e-5) == 0.0
    assert pytest.approx(transformed.y, abs=1e-5) == 1.0


def test_transform2d_rotation_around_pivot():
    # Rotate (10, 0) around pivot (5, 0) by 180 degrees -> should land at (0, 0)
    t = Transform2D.from_trs(
        translation=Vector2D(0.0, 0.0),
        rotation_deg=180.0,
        scale=Vector2D(1.0, 1.0),
        pivot=Vector2D(5.0, 0.0)
    )
    pt = Vector2D(10.0, 0.0)
    transformed = t.transform_point(pt)
    assert pytest.approx(transformed.x, abs=1e-5) == 0.0
    assert pytest.approx(transformed.y, abs=1e-5) == 0.0


def test_transform2d_composition():
    # Translate by (10, 0) then Rotate 90 deg vs Compose
    t_parent = Transform2D.from_translation(10.0, 0.0)
    t_child = Transform2D.from_translation(0.0, 5.0)
    
    # Combined parent * child
    t_combined = t_parent.compose(t_child)
    
    pt = Vector2D(0.0, 0.0)
    res = t_combined.transform_point(pt)
    assert pytest.approx(res.x) == 10.0
    assert pytest.approx(res.y) == 5.0


def test_easing_functions():
    # Linear endpoints
    assert ease_in_out_quad(0.0) == 0.0
    assert ease_in_out_quad(1.0) == 1.0
    assert ease_in_out_quad(0.5) == 0.5
    
    # Ease out back overshoots 1.0 before settling at 1.0
    assert pytest.approx(ease_out_back(0.0)) == 0.0
    assert pytest.approx(ease_out_back(1.0)) == 1.0
    assert ease_out_back(0.7) > 0.7
    
    # Spring lerp
    assert pytest.approx(spring_lerp(0.0, 100.0, 0.0)) == 0.0
    assert pytest.approx(spring_lerp(0.0, 100.0, 1.0)) == 100.0
