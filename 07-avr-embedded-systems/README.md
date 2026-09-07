# AVR Embedded Systems (ATmega16)

**Course:** ECTE333 — *Microcontroller Architecture & Applications*
**Hardware:** STK500 development board with an ATmega16 microcontroller

A series of bare-metal C programs building up register-level familiarity with the ATmega16: GPIO,
keypad scanning, USART serial communication, timers (overflow, input capture, PWM), and the 10-bit
ADC — culminating in a small combined system.

## Programs

- `code/keypad_7segment.c` — scans a 4x3 matrix keypad and mirrors the pressed key on a 7-segment
  display.
- `code/serial_comms.c` — USART send/receive over RS-232 to a HyperTerminal session; reads two
  integers from the terminal and prints their sum, difference, product, and quotient.
- `code/timer_interrupt_leds.c` — Timer1 overflow interrupt toggles LEDs on Port B every 4 seconds,
  alternating even/odd LEDs.
- `code/frequency_measurement.c` — Timer1 input-capture measures the period/frequency of an incoming
  signal and reports it over both USART and Port B.
- `code/pwm_signal_generator.c` — Timer1 Fast PWM (mode 14) generates a signal on OC1A with
  frequency and duty cycle entered live over USART.
- `code/adc_light_sensor.c` — reads a light sensor on the 10-bit ADC, converts the result to
  millivolts, and mirrors it on both USART and Port B LEDs.
- `code/light_activated_buzzer.c` — the capstone program: the user sets a delay (in seconds) on the
  keypad, confirmed with `#`; once set, the ADC continuously samples a light sensor, and when the
  reading drops below a threshold (dark), the program waits the configured delay and then sounds a
  buzzer.

## Visual assets

None available — the lab and final logbooks this code was drawn from are text-only, with no photos
of the physical STK500/breadboard setup.
