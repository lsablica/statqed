use std::env;
use std::fs::File;
use std::io::Cursor;
use std::sync::Arc;

use arrow::array::{Array, BinaryArray, Int64Array, RecordBatch, StringArray};
use arrow::datatypes::{DataType, Field, Schema};
use arrow::ipc::reader::{FileReader, StreamReader};
use arrow::ipc::writer::{FileWriter, StreamWriter};

fn fixture() -> RecordBatch {
    let schema = Arc::new(Schema::new(vec![
        Field::new("id", DataType::Int64, false),
        Field::new("label", DataType::Utf8, true),
        Field::new("payload", DataType::Binary, true),
    ]));
    RecordBatch::try_new(
        schema,
        vec![
            Arc::new(Int64Array::from(vec![1_i64, 2, 3])),
            Arc::new(StringArray::from(vec![
                Some("alpha"),
                None,
                Some("e\u{301}"),
            ])),
            Arc::new(BinaryArray::from(vec![
                Some(&b"\x00\xff"[..]),
                Some(&b""[..]),
                None,
            ])),
        ],
    )
    .expect("fixture is valid")
}

fn stream_bytes(batch: &RecordBatch) -> Vec<u8> {
    let mut bytes = Vec::new();
    {
        let mut writer = StreamWriter::try_new(&mut bytes, batch.schema().as_ref()).unwrap();
        writer.write(batch).unwrap();
        writer.finish().unwrap();
    }
    bytes
}

fn file_bytes(batch: &RecordBatch) -> Vec<u8> {
    let mut bytes = Vec::new();
    {
        let mut writer = FileWriter::try_new(&mut bytes, batch.schema().as_ref()).unwrap();
        writer.write(batch).unwrap();
        writer.finish().unwrap();
    }
    bytes
}

fn check_batch(batch: &RecordBatch) {
    let expected = fixture();
    assert_eq!(batch.schema().as_ref(), expected.schema().as_ref());
    assert_eq!(batch.num_rows(), 3);
    let ids = batch
        .column(0)
        .as_any()
        .downcast_ref::<Int64Array>()
        .unwrap();
    assert_eq!([ids.value(0), ids.value(1), ids.value(2)], [1, 2, 3]);
    let labels = batch
        .column(1)
        .as_any()
        .downcast_ref::<StringArray>()
        .unwrap();
    assert_eq!(labels.value(0), "alpha");
    assert!(labels.is_null(1));
    assert_eq!(labels.value(2), "e\u{301}");
    let payloads = batch
        .column(2)
        .as_any()
        .downcast_ref::<BinaryArray>()
        .unwrap();
    assert_eq!(payloads.value(0), b"\x00\xff");
    assert_eq!(payloads.value(1), b"");
    assert!(payloads.is_null(2));
}

fn command_self() {
    let batch = fixture();
    let stream_a = stream_bytes(&batch);
    let stream_b = stream_bytes(&batch);
    let file_a = file_bytes(&batch);
    let file_b = file_bytes(&batch);
    assert_eq!(stream_a, stream_b);
    assert_eq!(file_a, file_b);
    assert_ne!(stream_a, file_a);

    let mut stream_reader = StreamReader::try_new(Cursor::new(&stream_a), None).unwrap();
    let stream_batch = stream_reader.next().unwrap().unwrap();
    check_batch(&stream_batch);
    assert_eq!(stream_batch, batch);

    let mut file_reader = FileReader::try_new(Cursor::new(&file_a), None).unwrap();
    let file_batch = file_reader.next().unwrap().unwrap();
    check_batch(&file_batch);
    assert_eq!(file_batch, batch);

    println!("arrow_rs_version=59.1.0");
    println!("ipc_metadata_default=V5");
    println!("stream_repeat_equal=true");
    println!("file_repeat_equal=true");
    println!("stream_file_bytes_equal=false");
    println!("round_trip_equal=true");
    println!("stream_len={}", stream_a.len());
    println!("file_len={}", file_a.len());
}

fn command_read_file(path: &str) {
    let file = File::open(path).unwrap();
    let mut reader = FileReader::try_new(file, None).unwrap();
    let batch = reader.next().unwrap().unwrap();
    check_batch(&batch);
    assert!(reader.next().is_none());
    println!("rust_read_foreign_file=true");
}

fn command_write_file(path: &str) {
    let batch = fixture();
    let mut file = File::create(path).unwrap();
    let mut writer = FileWriter::try_new(&mut file, batch.schema().as_ref()).unwrap();
    writer.write(&batch).unwrap();
    writer.finish().unwrap();
    println!("rust_wrote_file=true");
}

fn command_reject_file(path: &str) {
    let file = File::open(path).unwrap();
    match FileReader::try_new(file, None) {
        Ok(_) => panic!("malformed Arrow file unexpectedly accepted"),
        Err(error) => println!("rust_rejected_malformed=true error={error}"),
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    match args.get(1).map(String::as_str) {
        Some("self") => command_self(),
        Some("read-file") => command_read_file(args.get(2).expect("path required")),
        Some("write-file") => command_write_file(args.get(2).expect("path required")),
        Some("reject-file") => command_reject_file(args.get(2).expect("path required")),
        _ => panic!(
            "usage: statqed-arrow-probe self|read-file PATH|write-file PATH|reject-file PATH"
        ),
    }
}
