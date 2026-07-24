; hello_raw.asm - Hello World using raw data
start:
    LDI16 R0, msg
    SYS 0, R0, R0
    HALT

msg:
    .word 0x0048   ; 'H'
    .word 0x0065   ; 'e'
    .word 0x006C   ; 'l'
    .word 0x006C   ; 'l'
    .word 0x006F   ; 'o'
    .word 0x002C   ; ','
    .word 0x0020   ; ' '
    .word 0x0057   ; 'W'
    .word 0x006F   ; 'o'
    .word 0x0072   ; 'r'
    .word 0x006C   ; 'l'
    .word 0x0064   ; 'd'
    .word 0x0021   ; '!'
    .word 0x000A   ; '\n'
    .word 0x0000   ; null
