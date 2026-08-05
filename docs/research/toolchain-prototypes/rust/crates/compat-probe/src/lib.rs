#![forbid(unsafe_code)]

use std::fmt::Write as FmtWrite;
use std::io::{Cursor, Read, Write as IoWrite};
use std::sync::Arc;

use arrow::array::{ArrayRef, Int64Array, StringArray};
use arrow::datatypes::{DataType, Field, Schema};
use arrow::ipc::writer::StreamWriter;
use arrow::record_batch::RecordBatch;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use zip::write::SimpleFileOptions;

/// Observations exercise candidate APIs only; they define no StatQED semantics.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct CandidateObservations {
    pub arrow_ipc_bytes: usize,
    pub archive_bytes: usize,
    pub blake3_hex: String,
    pub json_bytes: usize,
    pub rows: usize,
    pub sha256_hex: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
struct CandidateRecord {
    ids: Vec<i64>,
    labels: Vec<String>,
}

/// Exercise serialization, Arrow IPC, ZIP storage, and digest candidates.
///
/// The byte counts and digests are compatibility observations, not normative
/// encodings or artifact identifiers.
pub fn observe_candidate_apis()
-> Result<CandidateObservations, Box<dyn std::error::Error + Send + Sync>> {
    let candidate = CandidateRecord {
        ids: vec![1, 2, 3],
        labels: vec!["alpha".into(), "beta".into(), "gamma".into()],
    };
    let json = serde_json::to_vec(&candidate)?;

    let schema = Arc::new(Schema::new(vec![
        Field::new("id", DataType::Int64, false),
        Field::new("label", DataType::Utf8, false),
    ]));
    let columns: Vec<ArrayRef> = vec![
        Arc::new(Int64Array::from(candidate.ids.clone())),
        Arc::new(StringArray::from(candidate.labels.clone())),
    ];
    let batch = RecordBatch::try_new(Arc::clone(&schema), columns)?;
    let mut arrow_ipc = Vec::new();
    {
        let mut writer = StreamWriter::try_new(&mut arrow_ipc, &schema)?;
        writer.write(&batch)?;
        writer.finish()?;
    }

    let mut archive = Cursor::new(Vec::new());
    {
        let mut writer = zip::ZipWriter::new(&mut archive);
        writer.start_file("candidate.json", SimpleFileOptions::default())?;
        writer.write_all(&json)?;
        writer.finish()?;
    }
    archive.set_position(0);
    let archive_bytes = archive.get_ref().len();
    let mut reader = zip::ZipArchive::new(archive)?;
    let mut recovered = Vec::new();
    reader
        .by_name("candidate.json")?
        .read_to_end(&mut recovered)?;
    assert_eq!(recovered, json);

    let blake3_hex = blake3::hash(&json).to_hex().to_string();
    let sha256_bytes = Sha256::digest(&json);
    let mut sha256_hex = String::with_capacity(sha256_bytes.len() * 2);
    for byte in sha256_bytes {
        write!(&mut sha256_hex, "{byte:02x}")?;
    }

    Ok(CandidateObservations {
        arrow_ipc_bytes: arrow_ipc.len(),
        archive_bytes,
        blake3_hex,
        json_bytes: json.len(),
        rows: batch.num_rows(),
        sha256_hex,
    })
}

#[cfg(test)]
mod tests {
    use super::observe_candidate_apis;

    #[test]
    fn candidate_apis_execute_without_unsafe_project_code() {
        let observed = observe_candidate_apis().expect("candidate APIs should execute");
        assert_eq!(observed.rows, 3);
        assert!(observed.arrow_ipc_bytes > observed.json_bytes);
        assert!(observed.archive_bytes > observed.json_bytes);
        assert_eq!(observed.blake3_hex.len(), 64);
        assert_eq!(observed.sha256_hex.len(), 64);
    }
}
