# Streams radar data to be processed and manages sensor start/stop routines.
import threading, queue
from typing import List, Tuple, Optional

Point = Tuple[float, float, float, float, float]  # (x,y,z,v,snr)

class RadarReader(threading.Thread):
    def __init__(self, cfg_path: str = "1642config.cfg", max_queue: int = 2):
        super().__init__(daemon=True)
        self.cfg_path = cfg_path
        self.q: "queue.Queue[List[Point]]" = queue.Queue(maxsize=max_queue)
        self._stop_event = threading.Event()
        self._started_ok = False
        self._error: Optional[str] = None

    def run(self):
        try:
            import readData_AWR1642 as rdr
            for pts in rdr.stream_points(cfg_path=self.cfg_path, headless=True):
                if self._stop_event.is_set():
                    break
                if self.q.full():
                    try: self.q.get_nowait()
                    except queue.Empty: pass
                self.q.put_nowait(pts)
                self._started_ok = True
        except Exception as e:
            self._error = str(e)

    def stop(self):
        self._stop_event.set()

    def latest(self, timeout: float = 0.0) -> Optional[List[Point]]:
        try:
            return self.q.get(timeout=timeout)
        except queue.Empty:
            return None

    @property
    def started_ok(self) -> bool:
        return self._started_ok

    @property
    def error(self) -> Optional[str]:
        return self._error