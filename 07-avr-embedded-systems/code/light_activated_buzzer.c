/*
 * light_activated_buzzer.c
 * ATmega16 capstone program — user sets a delay (in seconds) on the 4x3
 * keypad, confirmed with '#'. Once set, the ADC continuously samples a
 * light sensor on ADC6; when the reading drops below 200 (dark), the
 * program waits the configured delay, then sounds a buzzer on Port D.6.
 *
 * ECTE333 - Microcontroller Architecture & Applications, University of Wollongong.
 */
#define F_CPU 1000000UL
#include <avr/io.h>
#include <util/delay.h>

void adc_init(void);
void buzzer_on(void);
void buzzer_off(void);
unsigned char read_keypad(void);
void wait_n_seconds(uint8_t n);
uint16_t read_adc(uint8_t channel);

void adc_init(void) {
    ADMUX = 0b01100110;  // ADC6, AVCC = 5V reference, left-adjusted
    ADCSRA = 0b10000110; // enable ADC, prescaler 64 (125 kHz ADC clock @ 1 MHz)
}

uint16_t read_adc(uint8_t channel) {
    ADMUX = (ADMUX & 0xF0) | (channel & 0x0F);
    ADCSRA |= (1 << ADSC);
    while (ADCSRA & (1 << ADSC)) { ; }
    return ADC;
}

void buzzer_on(void)  { PORTD |= (1 << PD6); }
void buzzer_off(void) { PORTD &= ~(1 << PD6); }

unsigned char read_keypad(void) {
    unsigned char key = 0;
    unsigned char port_value;
    unsigned char keypad_col_bit[3] = {6, 5, 4};
    unsigned char keypad_row_bit[4] = {3, 2, 1, 0};
    unsigned char keypad_key[3][4] = {
        {'1', '4', '7', '*'},
        {'2', '5', '8', '0'},
        {'3', '6', '9', '#'}
    };
    unsigned char col, row;

    DDRB = 0b11110000; // pins 0-3 input, pins 4-7 output

    for (col = 1; col <= 3; col++) {
        PORTB = ~(1 << (keypad_col_bit[col - 1]));
        asm volatile("nop");
        asm volatile("nop");
        port_value = PINB;
        for (row = 1; row <= 4; row++) {
            if ((port_value & (1 << (keypad_row_bit[row - 1]))) == 0)
                key = keypad_key[col - 1][row - 1];
        }
    }
    return key;
}

void wait_n_seconds(uint8_t n) {
    for (uint8_t i = 0; i < n; i++) {
        _delay_ms(1000);
    }
}

int main(void) {
    DDRB = 0xFF; // LEDs output
    DDRD = 0x40; // Port D.6 output (buzzer)
    adc_init();

    uint8_t delay = 0;
    uint8_t delay_set = 0;
    unsigned char key;

    while (1) {
        if (!delay_set) {
            // build up the delay value digit-by-digit until '#' confirms it
            key = read_keypad();
            if (key >= '0' && key <= '9') {
                delay = delay * 10 + (key - '0');
                _delay_ms(300); // debounce
            } else if (key == '#') {
                delay_set = 1;
            }
        } else {
            uint16_t adc_value = read_adc(6);
            if (adc_value < 200) { // dark
                wait_n_seconds(delay);
                buzzer_on();
            } else {
                buzzer_off();
            }
            _delay_ms(500);
        }
    }
    return 0;
}
