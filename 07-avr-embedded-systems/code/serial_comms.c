/*
 * serial_comms.c
 * ATmega16 USART — sends/receives characters over RS-232, then performs
 * simple integer arithmetic entered over a HyperTerminal session.
 * Baud rate 1200 bps assuming a 1 MHz clock.
 *
 * ECTE333 - Microcontroller Architecture & Applications, University of Wollongong.
 */
#include <avr/io.h>
#include <stdio.h>

void serial_init(void) {
    UCSRA = 0b00000000; // normal speed, disable multi-processor mode
    UCSRB = 0b00011000; // enable Tx and Rx, disable interrupts
    UCSRC = 0b10000110; // asynchronous, no parity, 1 stop bit, 8 data bits
    UBRRL = 0x33;        // 1200 bps @ 1 MHz clock
    UBRRH = 0x00;
}

int serial_send(char c, FILE *stream) {
    while ((UCSRA & (1 << UDRE)) == 0x00) { ; } // wait until UDR ready
    UDR = c;
    return 0;
}

int serial_receive(FILE *stream) {
    while ((UCSRA & (1 << RXC)) == 0x00) { ; } // wait until a byte arrives
    return UDR;
}

int main(void) {
    serial_init();
    stdout = fdevopen(serial_send, NULL);
    stdin = fdevopen(NULL, serial_receive);

    while (1) {
        unsigned int a, b;
        printf("\n\rEnter a = ");
        scanf("%u", &a);
        printf("a = %u\n\r", a);
        printf("\n\rEnter b = ");
        scanf("%u", &b);
        printf("b = %u\n\r", b);

        printf("\n\ra + b = %d\n\r", a + b);
        printf("a - b = %d\n\r", a - b);
        printf("a * b = %d\n\r", a * b);
        printf("a / b = %d\n\r", a / b);
    }
    return 0;
}
