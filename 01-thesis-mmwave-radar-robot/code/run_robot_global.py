# Main testing script to integrate radar with basic robot motion (stop when obstacle detected, move when obstacle not detected).
import time
from readData_AWR1642 import RadarThread
from global_planner import perform_global_scan, plan_path
from movement import move_forward, stop_all

# SETTINGS TO BE TUNED
MOVE_DURATION_SEC = 1.2      # how long the robot drives forward each run
MOVE_PWM_DUTY     = 98       # PWM duty cycle for movement
LOOP_DELAY_SEC    = 3.0      # time to wait between cycles (to let radar settle)

# Offset to compensate 'forward drive' being 45° ACW from robot forward
ALIGN_45_SEC   = 0.30   # seconds of rotate_cw()
POST_ALIGN_SEC = 0.30   # rotate back ACW by same amount

from movement import rotate_cw, rotate_acw, move_forward, stop_all
import time

def move_to_waypoint(waypoint):
    """
    Align -> move forward -> un-align.
    """
    wx, wy = waypoint
    print(f"[global] aligning +45° CW for {ALIGN_45_SEC:.2f}s")
    rotate_cw()
    time.sleep(ALIGN_45_SEC)
    stop_all(); time.sleep(0.05)

    print(f"[global] moving forward for {MOVE_DURATION_SEC:.2f}s toward {wx:.2f},{wy:.2f}")
    move_forward()
    time.sleep(MOVE_DURATION_SEC)
    stop_all(); time.sleep(0.05)

    print(f"[global] restoring heading -45° ACW for {POST_ALIGN_SEC:.2f}s")
    rotate_acw()
    time.sleep(POST_ALIGN_SEC)
    stop_all(); time.sleep(0.05)

    print("[global] segment complete.")


def main():
    radar = RadarThread()
    radar.start()
    time.sleep(2.0)  # let radar boot

    try:
        while True:
            print("\n[global] scanning 360° once (stitched)…")
            grid = perform_global_scan(radar)

            print("[global] computing path…")
            path = plan_path(grid)

            if path:
                print(f"[global] waypoint -> {path[-1]}")
                move_to_waypoint(path[-1])
            else:
                print("[global] no path found — staying put.")

            print("[global] loop complete. Waiting before next scan…")
            time.sleep(LOOP_DELAY_SEC)

    except KeyboardInterrupt:
        print("\n[global] stopping…")
        stop_all()
        radar.stop()
        print("[global] done.")


if __name__ == "__main__":
    main()