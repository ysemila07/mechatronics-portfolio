# High level robot movement commands including forward, backward, left, right, clockwise, anticlockwise.
import atexit
import RPi.GPIO as GPIO

# GPIO pins with motor driver connections (L298N)
A1_IN1 = 23
A1_IN2 = 24
A2_IN1 = 27
A2_IN2 = 22
ENA    = 25

B1_IN1 = 5
B1_IN2 = 6
B2_IN1 = 17
B2_IN2 = 16
ENB    = 12

motor_pins = [A1_IN1, A1_IN2, A2_IN1, A2_IN2, B1_IN1, B1_IN2, B2_IN1, B2_IN2]

# Internal state
_inited  = False
_pwm_a   = None
_pwm_b   = None
_pwm_on  = False

def _init_once():
    global _inited, _pwm_a, _pwm_b
    if _inited:
        return
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    for p in motor_pins:
        GPIO.setup(p, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(ENA, GPIO.OUT)
    GPIO.setup(ENB, GPIO.OUT)
    _pwm_a = GPIO.PWM(ENA, 1000)   # 1 kHz
    _pwm_b = GPIO.PWM(ENB, 1000)
    _inited = True

# Start or change PWM duty cycle
def _pwm_start(dc=98):
    """Start PWM if not running; otherwise just change duty."""
    global _pwm_on
    if not _inited:
        _init_once()
    if not _pwm_on:
        _pwm_a.start(dc); _pwm_b.start(dc)
        _pwm_on = True
    else:
        _pwm_a.ChangeDutyCycle(dc); _pwm_b.ChangeDutyCycle(dc)

# Stop PWM safely
def _pwm_stop():
    """Stop PWM safely if running."""
    global _pwm_on
    if _pwm_on:
        try: _pwm_a.ChangeDutyCycle(0)
        except Exception: pass
        try: _pwm_b.ChangeDutyCycle(0)
        except Exception: pass
        try: _pwm_a.stop()
        except Exception: pass
        try: _pwm_b.stop()
        except Exception: pass
        _pwm_on = False

# Set all pins to low
def _all_low():
    for p in motor_pins:
        GPIO.output(p, GPIO.LOW)

def stop_all():
    """Coast/stop and fully stop PWM (prevents cleanup errors)."""
    _init_once()
    _all_low()
    _pwm_stop()

# Functions for each movement
def move_forward(dc=98):
    _init_once(); _pwm_start(dc)
    GPIO.output(A1_IN1, GPIO.LOW);  GPIO.output(A1_IN2, GPIO.HIGH)
    GPIO.output(A2_IN1, GPIO.LOW);  GPIO.output(A2_IN2, GPIO.HIGH)
    GPIO.output(B1_IN1, GPIO.LOW);  GPIO.output(B1_IN2, GPIO.LOW)
    GPIO.output(B2_IN1, GPIO.LOW);  GPIO.output(B2_IN2, GPIO.LOW)

def move_backward(dc=98):
    _init_once(); _pwm_start(dc)
    GPIO.output(A1_IN1, GPIO.HIGH); GPIO.output(A1_IN2, GPIO.LOW)
    GPIO.output(A2_IN1, GPIO.HIGH); GPIO.output(A2_IN2, GPIO.LOW)
    GPIO.output(B1_IN1, GPIO.LOW);  GPIO.output(B1_IN2, GPIO.LOW)
    GPIO.output(B2_IN1, GPIO.LOW);  GPIO.output(B2_IN2, GPIO.LOW)

def move_left(dc=98):
    _init_once(); _pwm_start(dc)
    GPIO.output(A1_IN1, GPIO.LOW);  GPIO.output(A1_IN2, GPIO.LOW)
    GPIO.output(A2_IN1, GPIO.LOW);  GPIO.output(A2_IN2, GPIO.LOW)
    GPIO.output(B1_IN1, GPIO.HIGH); GPIO.output(B1_IN2, GPIO.LOW)
    GPIO.output(B2_IN1, GPIO.HIGH); GPIO.output(B2_IN2, GPIO.LOW)

def move_right(dc=98):
    _init_once(); _pwm_start(dc)
    GPIO.output(A1_IN1, GPIO.LOW);  GPIO.output(A1_IN2, GPIO.LOW)
    GPIO.output(A2_IN1, GPIO.LOW);  GPIO.output(A2_IN2, GPIO.LOW)
    GPIO.output(B1_IN1, GPIO.LOW);  GPIO.output(B1_IN2, GPIO.HIGH)
    GPIO.output(B2_IN1, GPIO.LOW);  GPIO.output(B2_IN2, GPIO.HIGH)

def rotate_acw(dc=80):
    """Anti-clockwise (left spin)."""
    _init_once(); _pwm_start(dc)
    GPIO.output(A1_IN1, GPIO.HIGH); GPIO.output(A1_IN2, GPIO.LOW)
    GPIO.output(A2_IN1, GPIO.LOW);  GPIO.output(A2_IN2, GPIO.HIGH)
    GPIO.output(B1_IN1, GPIO.HIGH); GPIO.output(B1_IN2, GPIO.LOW)
    GPIO.output(B2_IN1, GPIO.LOW);  GPIO.output(B2_IN2, GPIO.HIGH)

def rotate_cw(dc=80):
    """Clockwise (right spin)."""
    _init_once(); _pwm_start(dc)
    GPIO.output(A1_IN1, GPIO.LOW);  GPIO.output(A1_IN2, GPIO.HIGH)
    GPIO.output(A2_IN1, GPIO.HIGH); GPIO.output(A2_IN2, GPIO.LOW)
    GPIO.output(B1_IN1, GPIO.LOW);  GPIO.output(B1_IN2, GPIO.HIGH)
    GPIO.output(B2_IN1, GPIO.HIGH); GPIO.output(B2_IN2, GPIO.LOW)

# Convenience aliases used elsewhere (due to the change in conventions used in other codes)
forward = move_forward
backward = move_backward
left = move_left
right = move_right
rotate_ccw = rotate_acw

def shutdown_pwm():
    """Explicit call from mains to silence PWM.__del__ warnings."""
    _pwm_stop()

def cleanup():
    """One-shot cleanup."""
    try: stop_all()
    except Exception: pass
    try: GPIO.cleanup()
    except Exception: pass

atexit.register(cleanup)