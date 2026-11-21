.global _start
.section .text.entry, "ax"

_start:
    // Read hardware boot mode register at 0xFFFF000050FE4968
    mov     x0, #0x4968
    movk    x0, #0x50fe, lsl #16
    movk    x0, #0xffff, lsl #48
    ldrb    w0, [x0]
    and     w0, w0, #0xff

    // Verify if Fastboot mode requested (mode == 99 / 0x63)
    cmp     w0, #0x63
    b.ne    .Lexit

    // Setup stack frame
    stp     x29, x30, [sp, #-0x10]!
    mov     x29, sp

    // Store active bootmode flag into secondary buffer at 0xFFFF000050FD5510
    mov     x1, #0x5510
    movk    x1, #0x50fd, lsl #16
    movk    x1, #0xffff, lsl #48
    str     w0, [x1]

    // Invoke LittleKernel fastboot setup handler at 0xFFFF000050F7D684
    mov     x0, #0xd684
    movk    x0, #0x50f7, lsl #16
    movk    x0, #0xffff, lsl #48
    blr     x0

    // Invoke secondary fastboot registration routine at 0xFFFF000050F80CA0
    adrp    x0, 0xffff000050f02000
    mov     x1, #0xca0
    movk    x1, #0x50f8, lsl #16
    ldr     x0, [x0, #0x870]
    movk    x1, #0xffff, lsl #48
    blr     x1

    // Clean exit: restore original overwritten instruction and stack
    stur    xzr, [sp, #0x35]
    mov     w0, #0
    ldp     x29, x30, [sp], #0x10
    ret

.Lexit:
    // Restore original overwritten instruction before returning
    stur    xzr, [sp, #0x35]
    mov     w0, #0
    ret
