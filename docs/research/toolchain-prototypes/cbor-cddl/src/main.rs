use std::collections::BTreeMap;

use ciborium::value::{CanonicalValue, Value};
use minicbor::data::Type;

fn hex(bytes: &[u8]) -> String {
    bytes.iter().map(|byte| format!("{byte:02x}")).collect()
}

fn ciborium_length_first() -> Vec<u8> {
    let mut map = BTreeMap::new();
    map.insert(
        CanonicalValue::from(Value::Text(String::new())),
        Value::from(0),
    );
    map.insert(CanonicalValue::from(Value::from(24)), Value::from(0));
    let mut bytes = Vec::new();
    ciborium::ser::into_writer(&map, &mut bytes).unwrap();
    bytes
}

fn minicbor_order(integer_first: bool) -> Vec<u8> {
    let mut encoder = minicbor::Encoder::new(Vec::new());
    encoder.map(2).unwrap();
    if integer_first {
        encoder.u8(24).unwrap().u8(0).unwrap();
        encoder.str("").unwrap().u8(0).unwrap();
    } else {
        encoder.str("").unwrap().u8(0).unwrap();
        encoder.u8(24).unwrap().u8(0).unwrap();
    }
    encoder.into_writer()
}

fn nested(depth: usize) -> Vec<u8> {
    let mut bytes = vec![0x81; depth];
    bytes.push(0x00);
    bytes
}

fn main() {
    let core_421 = minicbor_order(true);
    let length_first_423 = minicbor_order(false);
    let ciborium = ciborium_length_first();
    assert_eq!(hex(&core_421), "a21818006000");
    assert_eq!(hex(&length_first_423), "a26000181800");
    assert_eq!(ciborium, length_first_423);
    assert_ne!(core_421, length_first_423);

    let duplicate = [0xa2, 0x01, 0x00, 0x01, 0x02];
    let decoded: Value = ciborium::de::from_reader(&duplicate[..]).unwrap();
    let duplicate_pairs = match decoded {
        Value::Map(pairs) => pairs.len(),
        _ => panic!("expected a map"),
    };
    assert_eq!(duplicate_pairs, 2);
    let mut mini = minicbor::Decoder::new(&duplicate);
    assert_eq!(mini.map().unwrap(), Some(2));
    let mut minicbor_pairs = Vec::new();
    for _ in 0..2 {
        minicbor_pairs.push((mini.u8().unwrap(), mini.u8().unwrap()));
    }
    assert_eq!(minicbor_pairs, vec![(1, 0), (1, 2)]);

    let indefinite = [0x9f, 0x01, 0x02, 0xff];
    let decoded: Value = ciborium::de::from_reader(&indefinite[..]).unwrap();
    let mut reencoded = Vec::new();
    ciborium::ser::into_writer(&decoded, &mut reencoded).unwrap();
    assert_eq!(reencoded, [0x82, 0x01, 0x02]);
    let mut mini = minicbor::Decoder::new(&indefinite);
    assert_eq!(mini.array().unwrap(), None);
    assert_eq!(mini.u8().unwrap(), 1);
    assert_eq!(mini.u8().unwrap(), 2);
    assert_eq!(mini.datatype().unwrap(), Type::Break);
    mini.skip().unwrap();

    let depth_127 = ciborium::de::from_reader::<Value, _>(&nested(127)[..]);
    let depth_128 = ciborium::de::from_reader::<Value, _>(&nested(128)[..]);
    println!("ciborium_version=0.2.2");
    println!("minicbor_version=2.3.0");
    println!("rfc8949_4_2_1_hex={}", hex(&core_421));
    println!("rfc8949_4_2_3_hex={}", hex(&length_first_423));
    println!("ciborium_canonicalvalue_hex={}", hex(&ciborium));
    println!(
        "ciborium_matches_length_first={}",
        ciborium == length_first_423
    );
    println!("minicbor_exposes_both_insertion_orders=true");
    println!("ciborium_duplicate_pair_count={duplicate_pairs}");
    println!("minicbor_duplicate_pair_count={}", minicbor_pairs.len());
    println!("ciborium_accepts_indefinite=true");
    println!("minicbor_accepts_indefinite=true");
    println!("ciborium_indefinite_reencode_hex={}", hex(&reencoded));
    println!("ciborium_depth_127_ok={}", depth_127.is_ok());
    println!("ciborium_depth_128_ok={}", depth_128.is_ok());

    let truncated = [0x18];
    let ciborium_error = ciborium::de::from_reader::<Value, _>(&truncated[..]).unwrap_err();
    let minicbor_error = minicbor::decode::<u8>(&truncated).unwrap_err();
    println!("ciborium_rejects_truncated=true error={ciborium_error}");
    println!("minicbor_rejects_truncated=true error={minicbor_error}");
}
