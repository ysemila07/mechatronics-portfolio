/*
 * frequency_measurement.c
 * ATmega16 Timer1 input-capture — measures the period/frequency of a signal
 * fed into D.6 (ICP1) and reports it over USART + PORTB, combining an
 * overflow count with the captured counter value to handle periods longer
 * than one 16-bit timer cycle.
 *
 * ECTE333 - Microcontroller Architecture & Applications, University of Wollongong.
 */
#include <avr/io.h>
#include <stdio.h>
#include <avr/interrupt.h>
#include <inttypes.h>

volatile uint32_t n;          // overflow count since last capture
volatile uint32_t period;     // measured period, us
volatile uint32_t frequency;  // measured frequency, Hz

ISR(TIMER1_OVF_vect) {
    n++;
}

ISR(TIMER1_CAPT_vect) { // rising edge on D.6
    uint32_t int_period = (uint32_t)ICR1;
    period = (n << 16) + int_period;
    frequency = 1000000UL / period;
    TCNT1 = 0;
    n = 0;
}

void serial_init(void) {
    UCSRA = 0b00000000;
    UCSRB = 0b00011000;
    UCSRC = 0b10000110;
    UBRRL = 0x33; // 1200 bps @ 1 MHz
    UBRRH = 0x00;
}

void timer_int(void) {
    TCCR1A = 0b00000000; // normal mode
    TCCR1B = 0b11000001; // noise canceller, rising edge, no prescaler
    TIMSK  = 0b00100100; // enable input-capture + overflow interrupts
}

int serial_send(char c, FILE *stream) {
    while ((UCSRA & (1 << UDRE)) == 0x00) { ; }
    UDR = c;
    return 0;
}

int main(void) {
    DDRB = 0xFF;
    stdout = fdevopen(serial_send, NULL);
    serial_init();
    timer_int();
    sei();

    while (1) {
        PORTB = ~(period >> 8);
        printf("Period = %ld us, Frequency = %ld Hz \r\n", period, frequency);
    }
    return 0;
}
