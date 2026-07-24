; neuristor_test.asm

start:
    LDI16 R1, 0xACE1
    LDI16 R2, cell_a
    ST    R2, R1

    LDI16 R7, fail_addr

    LD    R3, R2
    .word 0x6031
    JNZ   R7

    LD    R3, R2
    .word 0x6031
    JNZ   R7

    LD    R3, R2
    .word 0x6031
    JNZ   R7

    LDI16 R4, 0x1357
    LDI16 R5, cell_b
    ST    R5, R4

    LD    R3, R2
    .word 0x6031
    JNZ   R7

    LD    R6, R5
    .word 0x6064
    JNZ   R7

    LDI16 R0, pass_msg
    SYS   0, R0, R0
    HALT

fail_addr:
    LDI16 R0, fail_msg
    SYS   0, R0, R0
    HALT

pass_msg:
    .word 0x0050
    .word 0x0041
    .word 0x0053
    .word 0x0053
    .word 0x000A
    .word 0x0000

fail_msg:
    .word 0x0046
    .word 0x0041
    .word 0x0049
    .word 0x004C
    .word 0x000A
    .word 0x0000

cell_a:
    .word 0x0000

cell_b:
    .word 0x0000
