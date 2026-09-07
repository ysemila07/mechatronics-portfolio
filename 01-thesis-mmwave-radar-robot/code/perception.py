# Used to identify obstacles, apply mask/filtering and classify regions that are free to navigate.
from typing import List, Tuple, Dict, Optional
from collections import deque
import time

Point = Tuple[float, float, float, float, float]  # (x,y,z,v,snr)

# SETTINGS TO BE TUNED
MIN_FWD_STOP       = 0.20   # ignore super close objects
MAX_VALID_RANGE    = 1.20   # ignore anything beyond value

# Stop / caution corridors (ahead of robot, after transform)
X_HALF_WIDTH_STOP  = 0.20   # how wide from centre to trigger Y_STOP_MAX
Y_STOP_MAX         = 0.10   # stop when robot gets close to value
X_HALF_WIDTH_WARN  = 0.15   # awareness band for tracking nearby stuff
RELEASE_DISTANCE   = 0.15   # must clear beyond value to move again 

def nearest_front(points: List[Point]) -> Optional[Tuple[float, float]]:
    """Return (lat, fwd) of nearest point in forward corridor (for display/logic)."""
    nearest = None
    best_d = 1e9
    for (x, y, z, _, _) in points:
        lat, fwd = x, y
        if fwd <= MIN_FWD_STOP or fwd > MAX_VALID_RANGE:
            continue
        if abs(lat) <= X_HALF_WIDTH_WARN and fwd < best_d:
            best_d = fwd
            nearest = (float(lat), float(fwd))
    return nearest

def is_stop_frame(points: List[Point]) -> bool:
    """True if any point lies in the STOP corridor within Y_STOP_MAX."""
    for (x, y, z, _, _) in points:
        lat, fwd = x, y
        if fwd > MIN_FWD_STOP and fwd <= Y_STOP_MAX and fwd <= MAX_VALID_RANGE and abs(lat) <= X_HALF_WIDTH_STOP:
            return True
    return False

class StopGoController:
    """
    Sticky STOP with temporal hysteresis:
      - Any STOP-qualifying frame inside a short window latches STOP.
      - STOP holds for a minimum time before considering GO.
      - GO only when clearly released (distance > RELEASE_DISTANCE) or nothing seen for a while.
    """
    def __init__(self,
                 stop_window_sec: float = 0.9,    # lookback window for stop hits
                 stop_hits_needed: int = 1,       # how many stop frames to latch
                 min_stop_hold_sec: float = 1.5,  # minimum time to hold STOP
                 lost_frame_timeout: float = 1.2  # if nothing seen while stopped -> GO
                 ):
        self.stop_window_sec    = stop_window_sec
        self.stop_hits_needed   = stop_hits_needed
        self.min_stop_hold_sec  = min_stop_hold_sec
        self.lost_frame_timeout = lost_frame_timeout

        self.state = "go"
        self.stop_since = 0.0
        self.last_nearest: Optional[Tuple[float, float]] = None
        self._stop_hits = deque()   # timestamps of recent STOP frames
        self._last_frame_time = 0.0

    def update(self, pts: List[Point]) -> Dict[str, object]:
        now = time.time()
        self._last_frame_time = now

        if is_stop_frame(pts):
            self._stop_hits.append(now)

        # drop old hits outside the window
        while self._stop_hits and (now - self._stop_hits[0]) > self.stop_window_sec:
            self._stop_hits.popleft()

        self.last_nearest = nearest_front(pts)

        if self.state == "go":
            if len(self._stop_hits) >= self.stop_hits_needed:
                self.state = "stop"
                self.stop_since = now
        else:  # currently "stop"
            if (now - self.stop_since) >= self.min_stop_hold_sec:
                nearest = self.last_nearest
                if nearest is not None and nearest[1] >= RELEASE_DISTANCE:
                    self.state = "go"; self._stop_hits.clear()
                elif nearest is None and (now - self.stop_since) >= self.lost_frame_timeout:
                    self.state = "go"; self._stop_hits.clear()

        return {"action": self.state, "nearest": self.last_nearest}
