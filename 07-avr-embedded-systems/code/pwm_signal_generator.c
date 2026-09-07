/*
 * pwm_signal_generator.c
 * ATmega16 Timer1 Fast PWM (mode 14) — generates a PWM signal on OC1A
 * (Port D.5) with frequency and duty cycle entered live over USART.
 * Internal 1 MHz clock, no prescaler: ICR1 sets the period in
 * microseconds, OCR1A sets the high time.
 *
 * ECTE333 - Microcontroller Architecture & Applications, University of Wollongong.
 */
#include <avr/io.h>
#include <stdio.h>

volatile uint32_t freq;
volatile uint32_t period;
volatile uint32_t duty_cycle;
volatile uint32_t high_time;

void serial_init(void) {
    UCSRA = 0b00000000; // normal speed, disable multi-processor mode
    UCSRB = 0b00011000; // enable Tx and Rx, disable interrupts
    UCSRC = 0b10000110; // asynchronous, no parity, 1 stop bit, 8 data bits
    UBRRL = 0x33;        // 1200 bps @ 1 MHz clock
    UBRRH = 0x00;
}

void timer_int(void) {
    TCCR1A = 0b10000010; // Fast PWM 14 (0..ICR1); clear OC1A on compare match, set at 0
    TCCR1B = 0b00011001; // Fast PWM 14, internal clock, no prescaler
}

int serial_send(char c, FILE *stream) {
    while ((UCSRA & (1 << UDRE)) == 0x00) { ; }
    UDR = c;
    return 0;
}

int serial_receive(FILE *stream) {
    while ((UCSRA & (1 << RXC)) == 0x00) { ; }
    return UDR;
}

int main(void) {
    DDRD = 0b00100000; // Port D.5 (OC1A) as output, wired to oscilloscope
    serial_init();
    timer_int();
    stdout = fdevopen(serial_send, NULL);
    stdin = fdevopen(NULL, serial_receive);

    while (1) {
        printf("\r\n Enter the frequency in Hz: ");
        scanf("%ld", &freq);
        printf("\r\n Enter the duty cycle in percentage: ");
        scanf("%ld", &duty_cycle);

        period = (freq > 0) ? (1000000UL / freq) : 0; // avoid divide-by-zero
        ICR1 = period;

        // split calculation to avoid integer-division rounding to 0 below period=100
        if (period > 100) {
            high_time = (period / 100) * duty_cycle;
        } else {
            high_time = (period * duty_cycle) / 100;
        }
        OCR1A = high_time;

        printf("\r\n Period = %ld us, High Time = %ld us", period, high_time);
    }
}
