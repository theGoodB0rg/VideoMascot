from __future__ import annotations
import math
from typing import Tuple, Union
import numpy as np


class Vector2D:
    __slots__ = ("x", "y")

    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        self.x = float(x)
        self.y = float(y)

    def __repr__(self) -> str:
        return f"Vector2D({self.x:.2f}, {self.y:.2f})"

    def __add__(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: Union[float, int]) -> Vector2D:
        return Vector2D(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: Union[float, int]) -> Vector2D:
        return Vector2D(self.x / scalar, self.y / scalar)

    def magnitude(self) -> float:
        return math.hypot(self.x, self.y)

    def normalized(self) -> Vector2D:
        mag = self.magnitude()
        if mag == 0.0:
            return Vector2D(0.0, 0.0)
        return Vector2D(self.x / mag, self.y / mag)

    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)


class Transform2D:
    """Represents a 3x3 affine transformation matrix for 2D graphics & kinematics.
    
    Matrix layout:
    [ m00  m01  m02 ]   [ x ]   [ x' ]
    [ m10  m11  m12 ] * [ y ] = [ y' ]
    [  0    0    1  ]   [ 1 ]   [ 1  ]
    """
    __slots__ = ("matrix",)

    def __init__(self, matrix: np.ndarray) -> None:
        self.matrix = matrix

    @classmethod
    def identity(cls) -> Transform2D:
        return cls(np.eye(3, dtype=np.float64))

    @classmethod
    def from_translation(cls, tx: float, ty: float) -> Transform2D:
        m = np.eye(3, dtype=np.float64)
        m[0, 2] = tx
        m[1, 2] = ty
        return cls(m)

    @classmethod
    def from_rotation_deg(cls, angle_deg: float) -> Transform2D:
        rad = math.radians(angle_deg)
        c, s = math.cos(rad), math.sin(rad)
        m = np.array([
            [c, -s, 0.0],
            [s,  c, 0.0],
            [0.0, 0.0, 1.0]
        ], dtype=np.float64)
        return cls(m)

    @classmethod
    def from_scale(cls, sx: float, sy: float) -> Transform2D:
        m = np.array([
            [sx, 0.0, 0.0],
            [0.0, sy, 0.0],
            [0.0, 0.0, 1.0]
        ], dtype=np.float64)
        return cls(m)

    @classmethod
    def from_trs(
        cls,
        translation: Vector2D,
        rotation_deg: float,
        scale: Vector2D,
        pivot: Vector2D = Vector2D(0.0, 0.0)
    ) -> Transform2D:
        """Compose: Translate(translation + pivot) * Rotate(deg) * Scale(sx, sy) * Translate(-pivot)."""
        # 1. Translate to pivot
        t_to_pivot = cls.from_translation(-pivot.x, -pivot.y)
        # 2. Scale
        t_scale = cls.from_scale(scale.x, scale.y)
        # 3. Rotate
        t_rot = cls.from_rotation_deg(rotation_deg)
        # 4. Translate back + final position
        t_from_pivot = cls.from_translation(translation.x + pivot.x, translation.y + pivot.y)
        
        # Result = t_from_pivot * t_rot * t_scale * t_to_pivot
        return t_from_pivot.compose(t_rot).compose(t_scale).compose(t_to_pivot)

    def compose(self, child_transform: Transform2D) -> Transform2D:
        """Matrix multiplication: Self * Child (applies child in local space of self)."""
        return Transform2D(np.matmul(self.matrix, child_transform.matrix))

    def transform_point(self, pt: Vector2D) -> Vector2D:
        vec = np.array([pt.x, pt.y, 1.0], dtype=np.float64)
        res = np.dot(self.matrix, vec)
        return Vector2D(res[0], res[1])

    def inverse(self) -> Transform2D:
        return Transform2D(np.linalg.inv(self.matrix))

    def to_pillow_affine(self) -> Tuple[float, float, float, float, float, float]:
        """Returns 6-tuple (a, b, c, d, e, f) suitable for PIL.Image.transform(..., Image.AFFINE).
        
        Note: PIL uses inverse mapping from output image coordinate to input texture coordinate:
        x_in = a * x_out + b * y_out + c
        y_in = d * x_out + e * y_out + f
        """
        inv_m = np.linalg.inv(self.matrix)
        return (
            float(inv_m[0, 0]), float(inv_m[0, 1]), float(inv_m[0, 2]),
            float(inv_m[1, 0]), float(inv_m[1, 1]), float(inv_m[1, 2])
        )


# --- Easing Functions & Cubic Bezier Curves ---

class CubicBezier:
    """Parametric Cubic Bezier easing curve (CSS / Motion Graphics standard).
    
    P0 = (0, 0), P3 = (1, 1)
    Control points: P1 = (x1, y1), P2 = (x2, y2)
    """
    __slots__ = ("x1", "y1", "x2", "y2")

    def __init__(self, x1: float, y1: float, x2: float, y2: float) -> None:
        self.x1 = float(x1)
        self.y1 = float(y1)
        self.x2 = float(x2)
        self.y2 = float(y2)

    def _sample_curve_x(self, u: float) -> float:
        # 3*(1-u)^2*u*x1 + 3*(1-u)*u^2*x2 + u^3
        return 3.0 * (1.0 - u) * (1.0 - u) * u * self.x1 + 3.0 * (1.0 - u) * u * u * self.x2 + u * u * u

    def _sample_curve_y(self, u: float) -> float:
        return 3.0 * (1.0 - u) * (1.0 - u) * u * self.y1 + 3.0 * (1.0 - u) * u * u * self.y2 + u * u * u

    def _sample_curve_derivative_x(self, u: float) -> float:
        # Derivative of x with respect to u
        # 3*(1-u)^2*x1 + 6*(1-u)*u*(x2 - x1) + 3*u^2*(1 - x2)
        return (
            3.0 * (1.0 - u) * (1.0 - u) * self.x1
            + 6.0 * (1.0 - u) * u * (self.x2 - self.x1)
            + 3.0 * u * u * (1.0 - self.x2)
        )

    def _solve_curve_x(self, x: float, epsilon: float = 1e-6) -> float:
        # Newton-Raphson with fallback to bisection
        u = x
        for _ in range(8):
            curr_x = self._sample_curve_x(u) - x
            if abs(curr_x) < epsilon:
                return u
            d_x = self._sample_curve_derivative_x(u)
            if abs(d_x) < 1e-6:
                break
            u -= curr_x / d_x

        # Bisection fallback
        low, high = 0.0, 1.0
        u = x
        while low < high:
            curr_x = self._sample_curve_x(u)
            if abs(curr_x - x) < epsilon:
                return u
            if x > curr_x:
                low = u
            else:
                high = u
            u = 0.5 * (high + low)
            if abs(high - low) < epsilon:
                break
        return u

    def evaluate(self, t: float) -> float:
        """Evaluates easing progress y at time t in [0.0, 1.0]."""
        if t <= 0.0:
            return 0.0
        if t >= 1.0:
            return 1.0
        u = self._solve_curve_x(t)
        return self._sample_curve_y(u)


# Motion Design Industry Presets
SPRING_OVERSHOOT = CubicBezier(0.34, 1.56, 0.64, 1.0)
ANTICIPATION = CubicBezier(0.6, -0.28, 0.735, 0.045)
EASE_OUT_EXPO = CubicBezier(0.16, 1.0, 0.3, 1.0)
EASE_IN_OUT_QUINT = CubicBezier(0.83, 0.0, 0.17, 1.0)


def ease_in_out_quad(t: float) -> float:
    """Smooth ease in and out (quadratic). Input t in [0.0, 1.0]."""
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return 2.0 * t * t
    return -1.0 + (4.0 - 2.0 * t) * t


def ease_out_back(t: float, overshoot: float = 1.70158) -> float:
    """Ease out with slight bounce overshoot. Useful for snappy gestures and pop-ins."""
    if t <= 0.0:
        return 0.0
    if t >= 1.0:
        return 1.0
    t = t - 1.0
    return (t * t * ((overshoot + 1.0) * t + overshoot) + 1.0)


def spring_lerp(start: float, end: float, t: float, damping: float = 0.5, frequency: float = 4.0) -> float:
    """Damped spring interpolation for secondary motion (hair bounce, head bob)."""
    if t <= 0.0:
        return start
    if t >= 1.0:
        return end
    decay = math.exp(-damping * t * frequency)
    oscillation = math.cos(frequency * t * math.pi * 2.0)
    fraction = 1.0 - (decay * oscillation)
    return start + (end - start) * fraction

