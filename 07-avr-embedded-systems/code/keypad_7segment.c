/*
 * keypad_7segment.c
 * ATmega16 (STK500 board) — reads a 4x3 matrix keypad and mirrors the
 * pressed key on a 7-segment display.
 *
 * Keypad on PORTB: pins 0-3 input (rows), pins 4-7 output (columns).
 * 7-segment on PORTA (active high).
 *
 * ECTE333 - Microcontroller Architecture & Applications, University of Wollongong.
 */
#include <avr/io.h>

// Read the 4x3 keypad connected to PORTB and return the ASCII of the pressed key
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
        PORTB = ~(1 << (keypad_col_bit[col - 1])); // drive this column low
        asm volatile("nop");                        // short settle delay
        asm volatile("nop");
        port_value = PINB;                           // read back rows
        for (row = 1; row <= 4; row++) {
            if ((port_value & (1 << (keypad_row_bit[row - 1]))) == 0)
                key = keypad_key[col - 1][row - 1];
        }
    }
    return key;
}

// Map a key character onto a 7-segment display pattern and output it on PORTA
void display_7led(unsigned char key) {
    unsigned char led_pattern;
    DDRA = 0xFF;
    switch (key) {
        case '0': led_pattern = 0b00111111; break;
        case '1': led_pattern = 0b00000110; break;
        case '2': led_pattern = 0b01011011; break;
        case '3': led_pattern = 0b01001111; break;
        case '4': led_pattern = 0b01100110; break;
        case '5': led_pattern = 0b01101101; break;
        case '6': led_pattern = 0b01111101; break;
        case '7': led_pattern = 0b00000111; break;
        case '8': led_pattern = 0b01111111; break;
        case '9': led_pattern = 0b01100111; break;
        case '*': led_pattern = 0b01000110; break;
        case '#': led_pattern = 0b01100011; break;
        default:  led_pattern = 0; break; // no key pressed
    }
    PORTA = led_pattern;
}

int main(void) {
    while (1) {
        unsigned char key = read_keypad();
        display_7led(key);
    }
}
