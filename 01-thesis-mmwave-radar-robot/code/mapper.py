# Builds 2D occupancy grids from radar data to represent the environment around the robot.
from typing import List, Tuple
import numpy as np
import time
import math

Point = Tuple[float, float, float, float, float]  # (x,y,z,v,snr)

# SETTINGS TO BE TUNED
GRID_RES     = 0.12         # grid configs (meters)
GRID_HALF_W  = 1.5          
GRID_HALF_H  = 1.5          

# used in live dashboard
R_MIN        = 0.40         # ignore clutter below value
R_MAX        = 1.00         # ignore anything beyond value
MIN_SNR      = 15.0         # keep only strong radar points
MIN_ABS_VEL  = 0.0          # include static reflections

# Obstacle inflation & start bubble
INFLATE_RADIUS      = 0.12
START_CLEAR_RADIUS  = 0.25

def _grid_shape():
    W = int(np.ceil((2*GRID_HALF_W)/GRID_RES))
    H = int(np.ceil((2*GRID_HALF_H)/GRID_RES))
    return W, H

def _xy_to_idx(x: float, y: float):
    W, H = _grid_shape()
    gx = int(np.floor((x + GRID_HALF_W) / GRID_RES))
    gy = int(np.floor((y + GRID_HALF_H) / GRID_RES))
    return gx, gy

def _carve_free_disk(occ: np.ndarray, cx: int, cy: int, radius_cells: int):
    H, W = occ.shape
    for dy in range(-radius_cells, radius_cells+1):
        for dx in range(-radius_cells, radius_cells+1):
            if dx*dx + dy*dy <= radius_cells*radius_cells:
                x = cx + dx; y = cy + dy
                if 0 <= x < W and 0 <= y < H:
                    occ[y, x] = 0

def _rot2d(x: float, y: float, deg: float) -> Tuple[float,float]:
    th = math.radians(deg)
    ct, st = math.cos(th), math.sin(th)
    return (x*ct - y*st, x*st + y*ct)

# 360° scan accumulation
def accumulate_360_scan(
    radar,
    steps_per_rev: int,
    rotate_step_fn,
    dwell_sec: float = 0.40,
    settle_sec: float = 0.15,
    initial_heading_deg: float = 0.0,
    direction: str = "cw"
) -> List[Point]:
    """
    Perform one full revolution, accumulating points into a *global* robot-centric frame.
    Returns: list of (x_global, y_global, z, v, snr)
    """
    assert steps_per_rev >= 2
    step_angle = 360.0 / steps_per_rev
    step_sign  = +1.0 if direction.lower() == "cw" else -1.0
    heading = float(initial_heading_deg)

    pts_all: List[Point] = []

def _collect_once(heading_deg: float):
    nonlocal pts_all
    t0 = time.time()
    while (time.time() - t0) < dwell_sec:
        pts = radar.latest(timeout=0.0) or []
        if pts:
            # transform each point into global frame at current heading
            for (xr, yr, z, v, snr) in pts:
                # Range/SNR/velocity filtering (match dashboard)
                r = (xr**2 + yr**2) ** 0.5
                if r < R_MIN or r > R_MAX:
                    continue
                if snr < MIN_SNR:
                    continue
                if MIN_ABS_VEL > 0.0 and abs(v) < MIN_ABS_VEL:
                    continue

                # No offset now; radar == robot frame
                x_rob, y_rob = xr, yr

                # robot frame -> global frame at current heading
                xg, yg = _rot2d(x_rob, y_rob, heading_deg)
                pts_all.append((xg, yg, z, v, snr))
        time.sleep(0.01)

    # Initial sector
    _collect_once(heading)

    # Remaining sectors
    for _ in range(steps_per_rev - 1):
        if rotate_step_fn:
            rotate_step_fn()
        time.sleep(settle_sec)
        heading = (heading + step_sign * step_angle) % 360.0
        _collect_once(heading)

    return pts_all

# Building the grid
def build_occupancy_grid(points: List[Point]) -> np.ndarray:
    """
    Points are assumed to already be in the global robot-centric frame
    """
    W, H = _grid_shape()
    occ = np.zeros((H, W), dtype=np.uint8)

    for (x, y, z, _, peak) in points:
        if peak < MIN_PEAK:
            continue
        r = float(np.hypot(x, y))
        if r < MIN_FWD or r > MAX_RANGE:
            continue
        if abs(y) > GRID_HALF_H or abs(x) > GRID_HALF_W:
            continue
        gx, gy = _xy_to_idx(x, y)
        if 0 <= gx < W and 0 <= gy < H:
            occ[gy, gx] = 1

    # Inflate obstacles (square dilation)
    if INFLATE_RADIUS > 1e-6:
        k = int(np.ceil(INFLATE_RADIUS / GRID_RES))
        if k > 0:
            pad = np.pad(occ, k, mode='constant')
            inflated = np.zeros_like(pad)
            for dy in range(-k, k+1):
                for dx in range(-k, k+1):
                    inflated = np.maximum(inflated, np.roll(np.roll(pad, dy, axis=0), dx, axis=1))
            occ = inflated[k:-k, k:-k].astype(np.uint8)

    # Ensure start bubble is free
    start_gx, start_gy = _xy_to_idx(0.0, 0.0)
    _carve_free_disk(occ, start_gx, start_gy, int(round(START_CLEAR_RADIUS / GRID_RES)))

    return occ

def choose_exit_goal(occ: np.ndarray) -> Tuple[int, int]:
    H, W = occ.shape
    center_x = W // 2
    # Prefer far forward band with least obstacles near center
    for gy in range(H-1, int(0.55*H), -1):
        span = max(3, int(0.25 * W))
        xs = range(max(0, center_x - span), min(W, center_x + span))
        free_x = [gx for gx in xs if occ[gy, gx] == 0]
        if free_x:
            gx = min(free_x, key=lambda x: abs(x - center_x))
            return gx, gy
    # Fallback: any farthest free row
    for gy in range(H-1, 0, -1):
        free = np.where(occ[gy] == 0)[0]
        if free.size:
            gx = int(free[free.size//2])
            return gx, gy
    return center_x, H//2

def grid_to_xy(gx: int, gy: int) -> Tuple[float, float]:
    x = gx * GRID_RES - GRID_HALF_W + 0.5*GRID_RES
    y = gy * GRID_RES - GRID_HALF_H + 0.5*GRID_RES
    return x, y
