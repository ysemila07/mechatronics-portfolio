# Implement global path planning using 360º radar scan and determine optimal movement waypoints.
import math, time
import numpy as np
from debug_visual import save_debug_plot
from perception import MAX_VALID_RANGE

# SETTINGS TO BE TUNED
STEPS_PER_REV     = 14          # how many step pulses for ~360°
ROTATE_STEP_SEC   = 0.20        # duration of one rotation pulse
SETTLE_SEC        = 0.15        # pause after each step
SCAN_DWELL_SEC    = 0.40        # time to collect points each step
SCAN_DIRECTION    = "cw"        # spin direction

GRID_RES          = 0.12        # grid configs (meters)
GRID_HALF_W       = 1.5
GRID_HALF_H       = 1.5

from movement import rotate_cw, rotate_acw, stop_all

def perform_global_scan(radar):
    """
    Spins the robot and radar to collect 360° environment map.
    Returns: 2D numpy grid of obstacle intensities.
    """
    grid_w = int((GRID_HALF_W * 2) / GRID_RES)
    grid_h = int((GRID_HALF_H * 2) / GRID_RES)
    grid = np.zeros((grid_h, grid_w), dtype=np.float32)

    print(f"[global] Performing {STEPS_PER_REV} scan steps…")
    for step in range(STEPS_PER_REV):
        print(f"[global] Step {step+1}/{STEPS_PER_REV}")

        # collect data for dwell duration
        pts_all = []
        start_t = time.time()
        while time.time() - start_t < SCAN_DWELL_SEC:
            pts = radar.get_points()
            if pts:
                pts_all.extend(pts)
            time.sleep(0.05)

        # convert detections to grid
        for (x, y, z, v, snr) in pts_all:
            r = math.hypot(x, y)
            if 0.05 < r < MAX_VALID_RANGE:
                gx = int(grid_w / 2 + x / GRID_RES)
                gy = int(grid_h / 2 + y / GRID_RES)
                if 0 <= gx < grid_w and 0 <= gy < grid_h:
                    grid[gy, gx] = min(255, grid[gy, gx] + snr)

        # rotate to next sector
        if SCAN_DIRECTION == "cw":
            rotate_cw()
        else:
            rotate_acw()
        time.sleep(ROTATE_STEP_SEC)
        stop_all()
        time.sleep(SETTLE_SEC)

    # save plot
    save_debug_plot(grid, GRID_RES, path=None)
    return grid


# Path planner
def plan_path(grid):
    """
    Strategy: finds clear corridor toward top of map.
    Returns: list of waypoints [(x, y), ...]
    """
    h, w = grid.shape
    start = (w // 2, h // 2)
    goal_y = h - 1
    goal_x = w // 2

    # Simple upward corridor detection
    clear_cols = np.where(np.mean(grid[int(h*0.6):, :], axis=0) < 2.0)[0]
    if len(clear_cols) > 0:
        goal_x = int(np.median(clear_cols))

    print(f"[global] grid size: {w}x{h}, start={start}, goal=({goal_x}, {goal_y})")

    path = []
    for gy in range(start[1], goal_y, 3):
        path.append(((goal_x - w/2) * GRID_RES, (gy - h/2) * GRID_RES))

    if path:
        return [path[-1]]  # final point
    return []