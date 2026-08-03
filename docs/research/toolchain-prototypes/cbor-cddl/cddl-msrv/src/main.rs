fn main() {
    let _ = cddl::cddl_from_str("probe = uint", true).expect("minimal CDDL parses");
}
