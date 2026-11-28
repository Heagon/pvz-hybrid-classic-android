SECTIONS
{
    . = 0x00b52000;
    .text : {
        *(.text.entry)
        *(.text*)
        *(.rodata*)
        *(.rdata*)
    }
    .data : {
        *(.data*)
    }
    _blob_end = .;

    . = 0x00b58000;
    .bss (NOLOAD) : {
        *(.bss*)
        *(COMMON)
    }
    _bss_end = .;

    /DISCARD/ : {
        *(.eh_frame*)
        *(.comment*)
        *(.rdata$zzz*)
    }
}
