# Generates 2D visual maps for path planning.
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def save_debug_plot(grid: np.ndarray,
                    grid_res: float,
                    path=None,
                    fname: str = "debug_map.png"):
    """
    Save plot.
      - grid: 2D numpy array (H x W) of intensities
      - grid_res: meters per cell
      - path: list of (x,y) waypoints in meters (robot frame, x lateral, y forward)
      - fname: filename
    """
    H, W = grid.shape
    extent = (-W/2*grid_res, W/2*grid_res, -H/2*grid_res, H/2*grid_res)

    # labels
    plt.figure(figsize=(6, 6), dpi=120)
    plt.imshow(grid, origin="lower", extent=extent, aspect="equal")
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.title("Debug Map")

    # draw robot at origin
    plt.scatter([0], [0], marker='x')

    # draw path if provided and iterable of (x,y)
    if path is not None:
        try:
            if len(path) > 0 and hasattr(path[0], "__iter__"):
                px, py = zip(*path)
                plt.plot(px, py)
        except Exception:
            # ignore bad path inputs
            pass

    # range rings for quick scale
    for r in (0.1, 0.25, 0.35, 0.5, 1.0, 1.5):
        circ = plt.Circle((0, 0), r, fill=False, linewidth=0.5)
        plt.gca().add_patch(circ)

    plt.tight_layout()
    plt.savefig(fname)
    plt.close()