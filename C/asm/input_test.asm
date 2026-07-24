; input_test.asm

start:
    ; Test 1: Read character
    LDI16 R0, msg1
    SYS 0, R0, R0
    SYS 4, R1, R1
    LDI16 R0, msg1_result
    SYS 0, R0, R0
    SYS 2, R1, R1
    LDI R0, 10
    SYS 2, R0, R0

    ; Test 2: Read integer
    LDI16 R0, msg2
    SYS 0, R0, R0
    SYS 5, R1, R1
    LDI16 R0, msg2_result
    SYS 0, R0, R0
    SYS 1, R1, R1
    LDI R0, 10
    SYS 2, R0, R0

    ; Test 3: Read string
    LDI16 R0, msg3
    SYS 0, R0, R0
    LDI16 R0, buffer
    LDI R1, 32
    SYS 6, R0, R1
    LDI16 R0, msg3_result
    SYS 0, R0, R0
    LDI16 R0, buffer
    SYS 0, R0, R0
    LDI R0, 10
    SYS 2, R0, R0

    ; Done
    LDI16 R0, done_msg
    SYS 0, R0, R0
    HALT

; ============================================================
; Data section - ALL strings as .word
; ============================================================

msg1:
    .word 0x0054  ; T
    .word 0x0065  ; e
    .word 0x0073  ; s
    .word 0x0074  ; t
    .word 0x0020  ; space
    .word 0x0031  ; 1
    .word 0x003A  ; :
    .word 0x0020  ; space
    .word 0x0050  ; P
    .word 0x0072  ; r
    .word 0x0065  ; e
    .word 0x0073  ; s
    .word 0x0073  ; s
    .word 0x0020  ; space
    .word 0x0061  ; a
    .word 0x006E  ; n
    .word 0x0079  ; y
    .word 0x0020  ; space
    .word 0x006B  ; k
    .word 0x0065  ; e
    .word 0x0079  ; y
    .word 0x003A  ; :
    .word 0x0020  ; space
    .word 0x0000  ; null

msg1_result:
    .word 0x0059  ; Y
    .word 0x006F  ; o
    .word 0x0075  ; u
    .word 0x0020  ; space
    .word 0x0070  ; p
    .word 0x0072  ; r
    .word 0x0065  ; e
    .word 0x0073  ; s
    .word 0x0073  ; s
    .word 0x0065  ; e
    .word 0x0064  ; d
    .word 0x003A  ; :
    .word 0x0020  ; space
    .word 0x0000  ; null

msg2:
    .word 0x0054  ; T
    .word 0x0065  ; e
    .word 0x0073  ; s
    .word 0x0074  ; t
    .word 0x0020  ; space
    .word 0x0032  ; 2
    .word 0x003A  ; :
    .word 0x0020  ; space
    .word 0x0045  ; E
    .word 0x006E  ; n
    .word 0x0074  ; t
    .word 0x0065  ; e
    .word 0x0072  ; r
    .word 0x0020  ; space
    .word 0x0061  ; a
    .word 0x0020  ; space
    .word 0x006E  ; n
    .word 0x0075  ; u
    .word 0x006D  ; m
    .word 0x0062  ; b
    .word 0x0065  ; e
    .word 0x0072  ; r
    .word 0x003A  ; :
    .word 0x0020  ; space
    .word 0x0000  ; null

msg2_result:
    .word 0x0059  ; Y
    .word 0x006F  ; o
    .word 0x0075  ; u
    .word 0x0020  ; space
    .word 0x0065  ; e
    .word 0x006E  ; n
    .word 0x0074  ; t
    .word 0x0065  ; e
    .word 0x0072  ; r
    .word 0x0065  ; e
    .word 0x0064  ; d
    .word 0x003A  ; :
    .word 0x0020  ; space
    .word 0x0000  ; null

msg3:
    .word 0x0054  ; T
    .word 0x0065  ; e
    .word 0x0073  ; s
    .word 0x0074  ; t
    .word 0x0020  ; space
    .word 0x0033  ; 3
    .word 0x003A  ; :
    .word 0x0020  ; space
    .word 0x0045  ; E
    .word 0x006E  ; n
    .word 0x0074  ; t
    .word 0x0065  ; e
    .word 0x0072  ; r
    .word 0x0020  ; space
    .word 0x0061  ; a
    .word 0x0020  ; space
    .word 0x0073  ; s
    .word 0x0074  ; t
    .word 0x0072  ; r
    .word 0x0069  ; i
    .word 0x006E  ; n
    .word 0x0067  ; g
    .word 0x003A  ; :
    .word 0x0020  ; space
    .word 0x0000  ; null

msg3_result:
    .word 0x0059  ; Y
    .word 0x006F  ; o
    .word 0x0075  ; u
    .word 0x0020  ; space
    .word 0x0065  ; e
    .word 0x006E  ; n
    .word 0x0074  ; t
    .word 0x0065  ; e
    .word 0x0072  ; r
    .word 0x0065  ; e
    .word 0x0064  ; d
    .word 0x003A  ; :
    .word 0x0020  ; space
    .word 0x0000  ; null

done_msg:
    .word 0x0041  ; A
    .word 0x006C  ; l
    .word 0x006C  ; l
    .word 0x0020  ; space
    .word 0x0074  ; t
    .word 0x0065  ; e
    .word 0x0073  ; s
    .word 0x0074  ; t
    .word 0x0073  ; s
    .word 0x0020  ; space
    .word 0x0063  ; c
    .word 0x006F  ; o
    .word 0x006D  ; m
    .word 0x0070  ; p
    .word 0x006C  ; l
    .word 0x0065  ; e
    .word 0x0074  ; t
    .word 0x0065  ; e
    .word 0x0021  ; !
    .word 0x000A  ; newline
    .word 0x0000  ; null

buffer:
    .word 0,0,0,0,0,0,0,0
    .word 0,0,0,0,0,0,0,0
