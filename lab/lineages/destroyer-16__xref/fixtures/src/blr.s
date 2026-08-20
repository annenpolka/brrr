// Indirect blr to getenv. xref only scans bl/b immediates.
        .text
        .globl _main
        .align 2
_main:
        stp     x29, x30, [sp, #-16]!
        adrp    x16, _getenv@GOTPAGE
        ldr     x16, [x16, _getenv@GOTPAGEOFF]
        adrp    x0, Lname@PAGE
        add     x0, x0, Lname@PAGEOFF
        blr     x16
        mov     w0, #0
        ldp     x29, x30, [sp], #16
        ret

        .section __TEXT,__cstring,cstring_literals
Lname:
        .asciz  "BLR_ENV_NAME"
