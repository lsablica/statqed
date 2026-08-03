#![forbid(unsafe_code)]

pub fn deliberately_rejected_unsafe_block() -> u8 {
    let byte = 7_u8;
    let pointer = &raw const byte;
    // This fixture must fail because the project policy forbids unsafe code.
    unsafe { *pointer }
}
