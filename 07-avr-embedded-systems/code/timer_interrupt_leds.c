/*
 * timer_interrupt_leds.c
 * ATmega16 Timer1 overflow interrupt used to toggle LEDs on PORTB every
 * 4 seconds, alternating even/odd LEDs. No prescaler, 1 MHz internal clock:
 * 4 s = 61 overflows of the 16-bit timer (65,536 counts per overflow).
 *
 * ECTE333 - Microcontroller Architecture & Applications, University of Wollongong.
 */
#include <avr/io.h>
#include <avr/interrupt.h>

volatile int overflow_count;

ISR(TIMER1_OVF_vect) {
    overflow_count++;
    if (overflow_count >= 61) { // ~4 s: 4 / (65536 * 1e-6) = 61
        overflow_count = 0;
        PORTB = ~PORTB; // invert all of PORTB
    }
}

int main(void) {
    DDRB = 0xFF;
    PORTB = 0b10101010; // start with even LEDs on
    overflow_count = 0;

    sei();
    TCCR1A = 0b00000000; // normal mode
    TCCR1B = 0b00000001; // no prescaler, internal clock
    TIMSK  = 0b00000100; // enable Timer1 overflow interrupt

    while (1) { ; }
    return 0;
}
