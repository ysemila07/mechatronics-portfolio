/*
 * adc_light_sensor.c
 * ATmega16 10-bit ADC — samples a light sensor on ADC6 (Port A), converts
 * the reading to millivolts, prints it over USART, and mirrors the
 * inverted digital value on Port B LEDs.
 *
 * ECTE333 - Microcontroller Architecture & Applications, University of Wollongong.
 */
#include <avr/io.h>
#include <stdio.h>
#include <inttypes.h>

int serial_send(char c, FILE *stream) {
    while ((UCSRA & (1 << UDRE)) == 0x00) { ; }
    UDR = c;
    return 0;
}

void serial_init(void) { // 2400 bps
    UCSRA = 0b00000000;
    UCSRB = 0b00011000;
    UCSRC = 0b10000110;
    UBRRL = 0x19; // 2400 bps @ 1 MHz clock
    UBRRH = 0x00;
}

int main(void) {
    DDRA = 0x00; // Port A input (sensor)
    DDRB = 0xFF; // Port B output (LEDs)
    serial_init();
    stdout = fdevopen(serial_send, NULL);

    // ADC6, AVCC = 5V reference, left-adjusted result
    ADMUX = 0b01100110;
    ADCSRA = 0b10000001; // enable ADC, no auto-trigger, no interrupt, prescaler 2

    while (1) {
        ADCSRA |= 0b01000000;             // start conversion
        while (ADCSRA & 0b01000000) { ; } // wait until conversion complete

        uint32_t low = ADCL;
        uint32_t high = ADCH;
        uint32_t d = (high << 2) + ((low & 0b11000000) >> 6); // 10-bit result, left-adjusted
        uint32_t input_voltage = (d * 5000) / 1024;           // scale to mV (5V reference)

        printf("ADC digital value = %ld, input voltage = %ld (mV) \r \n", d, input_voltage);
        PORTB = ~(d); // mirror on LEDs
    }
    return 0;
}
