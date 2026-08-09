//! Experimental, bounded deterministic-CBOR prototype for `StatQED` SQ-0005.
//!
//! This crate is deliberately isolated from the production backend.  The strict
//! parser below retains ordered raw map entries and source spans before any
//! duplicate check.  [`minicbor`] is used only for the library-backed preferred
//! encoder path; its native value or map types do not define this profile.

#![forbid(unsafe_code)]

use core::cmp::Ordering;
use core::fmt;
use core::ops::Range;
use minicbor::Encoder;
use minicbor::encode::Write as CborWrite;
use serde_json::{Map as JsonMap, Value as JsonValue};
use sha2::{Digest, Sha256};

/// Candidate profile identifier used by this prototype.
pub const PROFILE_ID: &str = "statqed.cbor-core.v1";
/// Fixed framing identifier used by the data-free digest experiment.
pub const FRAMING_ID: &str = "statqed.digest-lp.v1";
/// Fixed framing magic and version. It is followed by six u32-be length frames.
pub const FRAME_MAGIC: &[u8] = b"StatQED-Digest\0";
/// The only digest algorithm identifier implemented by the prototype.
pub const SHA256_ALGORITHM_ID: &str = "sha-256";

const PROFILE_MAX_INPUT_BYTES: usize = 1_048_576;
const PROFILE_MAX_OUTPUT_BYTES: usize = 1_048_576;
const PROFILE_MAX_STRING_BYTES: usize = 65_536;
const PROFILE_MAX_ARRAY_ITEMS: usize = 1_024;
const PROFILE_MAX_MAP_ENTRIES: usize = 1_024;
const PROFILE_MAX_TOTAL_ITEMS: usize = 4_096;
const PROFILE_MAX_NESTING_DEPTH: usize = 32;
const PROFILE_MAX_DIAGNOSTIC_BYTES: usize = 4_096;
const PROFILE_MAX_DIGEST_FRAME_BYTES: usize = 1_049_255;

/// Lowest integer accepted by direct CBOR major types 0 and 1.
pub const MIN_INTEGER: i128 = -(1_i128 << 64);
/// Highest integer accepted by direct CBOR major types 0 and 1.
pub const MAX_INTEGER: i128 = u64::MAX as i128;

/// Stable classification of a prototype failure.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum ResultClass {
    /// The byte stream is not one complete well-formed CBOR item.
    WellFormedness,
    /// The stream is well formed but violates CBOR/application key validity.
    Validity,
    /// The item violates the selected deterministic byte profile.
    DeterministicProfile,
    /// The valid deterministic item has an unexpected application shape.
    Expectedness,
    /// Reserved for the separate CDDL structural checker.
    CddlShape,
    /// A semantic producer value is invalid or explicitly unsupported.
    SemanticValidity,
    /// A configured or implementation hard resource bound was exceeded.
    ResourceLimit,
    /// Generic data-free digest framing or algorithm selection failed.
    DigestVerification,
}

impl ResultClass {
    /// Return the stable snake-case wire spelling.
    #[must_use]
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::WellFormedness => "well_formedness",
            Self::Validity => "validity",
            Self::DeterministicProfile => "deterministic_profile",
            Self::Expectedness => "expectedness",
            Self::CddlShape => "cddl_shape",
            Self::SemanticValidity => "semantic_validity",
            Self::ResourceLimit => "resource",
            Self::DigestVerification => "digest_verification",
        }
    }
}

/// Stable error returned by all prototype operations.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Failure {
    /// Result class; stable diagnostic spelling is available through [`ResultClass::as_str`].
    pub class: ResultClass,
    /// Stable symbolic failure code.
    pub code: &'static str,
    /// Byte offset when one is meaningful, otherwise zero.
    pub offset: usize,
}

impl Failure {
    const fn new(class: ResultClass, code: &'static str, offset: usize) -> Self {
        Self {
            class,
            code,
            offset,
        }
    }
}

impl fmt::Display for Failure {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            formatter,
            "{}:{}@{}",
            self.class.as_str(),
            self.code,
            self.offset
        )
    }
}

impl std::error::Error for Failure {}

/// Explicit resource limits. Defaults are the candidate profile values.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Limits {
    /// Maximum input CBOR bytes.
    pub max_input_bytes: usize,
    /// Maximum simultaneously open array, map, or attempted-tag levels.
    pub max_nesting_depth: usize,
    /// Maximum items in one array.
    pub max_array_items: usize,
    /// Maximum entries in one map.
    pub max_map_entries: usize,
    /// Maximum total parsed or encoded value nodes, including map keys.
    pub max_total_items: usize,
    /// Maximum byte-string payload length.
    pub max_byte_string_bytes: usize,
    /// Maximum UTF-8 text payload length in bytes.
    pub max_text_string_bytes: usize,
    /// Maximum canonical output bytes.
    pub max_output_bytes: usize,
    /// Maximum complete digest-frame bytes.
    pub max_digest_frame_bytes: usize,
    /// Maximum non-normative diagnostic JSON output bytes.
    pub max_diagnostic_output_bytes: usize,
}

impl Default for Limits {
    fn default() -> Self {
        Self {
            max_input_bytes: 1024 * 1024,
            max_nesting_depth: 32,
            max_array_items: 1024,
            max_map_entries: 1024,
            max_total_items: 4096,
            max_byte_string_bytes: 64 * 1024,
            max_text_string_bytes: 64 * 1024,
            max_output_bytes: 1024 * 1024,
            max_digest_frame_bytes: PROFILE_MAX_DIGEST_FRAME_BYTES,
            max_diagnostic_output_bytes: 4096,
        }
    }
}

impl Limits {
    fn check(&self) -> Result<(), Failure> {
        let failure = if self.max_input_bytes > PROFILE_MAX_INPUT_BYTES {
            Some((ResultClass::ResourceLimit, "resource.input_bytes"))
        } else if self.max_output_bytes > PROFILE_MAX_OUTPUT_BYTES {
            Some((ResultClass::ResourceLimit, "resource.output_bytes"))
        } else if self.max_byte_string_bytes > PROFILE_MAX_STRING_BYTES
            || self.max_text_string_bytes > PROFILE_MAX_STRING_BYTES
        {
            Some((ResultClass::ResourceLimit, "resource.string_bytes"))
        } else if self.max_array_items > PROFILE_MAX_ARRAY_ITEMS {
            Some((ResultClass::ResourceLimit, "resource.array_items"))
        } else if self.max_map_entries > PROFILE_MAX_MAP_ENTRIES {
            Some((ResultClass::ResourceLimit, "resource.map_entries"))
        } else if self.max_total_items > PROFILE_MAX_TOTAL_ITEMS {
            Some((ResultClass::ResourceLimit, "resource.total_items"))
        } else if self.max_nesting_depth > PROFILE_MAX_NESTING_DEPTH {
            Some((ResultClass::ResourceLimit, "resource.depth"))
        } else if self.max_diagnostic_output_bytes > PROFILE_MAX_DIAGNOSTIC_BYTES {
            Some((ResultClass::ResourceLimit, "resource.diagnostic_bytes"))
        } else if self.max_digest_frame_bytes > PROFILE_MAX_DIGEST_FRAME_BYTES {
            Some((ResultClass::DigestVerification, "digest.length"))
        } else {
            None
        };
        match failure {
            Some((class, code)) => Err(Failure::new(class, code, 0)),
            None => Ok(()),
        }
    }
}

/// Map-key ordering mode.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum MapOrder {
    /// RFC 8949 section 4.2.1 bytewise lexicographic ordering; candidate default.
    CoreLexicographic,
    /// RFC 8949 section 4.2.3 length-first ordering, retained only for diagnostics.
    DiagnosticLengthFirst,
}

/// Configurable narrow profile.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Profile {
    /// Explicit resource bounds.
    pub limits: Limits,
    /// Candidate or diagnostic map ordering.
    pub map_order: MapOrder,
}

impl Default for Profile {
    fn default() -> Self {
        Self {
            limits: Limits::default(),
            map_order: MapOrder::CoreLexicographic,
        }
    }
}

/// Accepted semantic integer or text map key.
#[derive(Clone, Debug, Eq, Hash, PartialEq)]
pub enum Key {
    /// Signed basic integer key.
    Integer(i128),
    /// UTF-8 text key, preserved exactly without Unicode normalization.
    Text(String),
}

/// One semantic map entry. Order is retained, although canonical encoding sorts keys.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct MapEntry {
    /// Integer or text key.
    pub key: Key,
    /// Entry value.
    pub value: Value,
}

/// Narrow semantic value model accepted by the v1 prototype.
#[derive(Clone, Debug, Eq, PartialEq)]
pub enum Value {
    /// Signed basic integer.
    Integer(i128),
    /// Definite byte string.
    Bytes(Vec<u8>),
    /// Definite valid UTF-8 text, with code-point sequence preserved.
    Text(String),
    /// Definite array.
    Array(Vec<Self>),
    /// Definite map with integer/text keys.
    Map(Vec<MapEntry>),
    /// Boolean.
    Boolean(bool),
    /// Null.
    Null,
}

/// Preferred-head observation retained by the raw parser.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum HeadForm {
    /// Shortest permitted argument form.
    Preferred,
    /// A basic integer used a longer-than-needed argument.
    NonPreferredInteger,
    /// A definite collection or string used a longer-than-needed length.
    NonPreferredLength,
    /// A tag number used a longer-than-needed argument.
    NonPreferredTag,
    /// An indefinite-length string or container head.
    Indefinite,
}

/// Pre-lossy raw node with a source span.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct RawNode {
    /// Complete encoded byte range in [`RawDocument::source`].
    pub span: Range<usize>,
    /// Preferred-argument observation for this item head.
    pub head_form: HeadForm,
    /// Parsed value, without native-map conversion.
    pub kind: RawKind,
}

/// One ordered raw map entry. Duplicates remain present here.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct RawMapEntry {
    /// Raw key and its exact source span.
    pub key: RawNode,
    /// Raw value and its exact source span.
    pub value: RawNode,
}

/// Lossless-within-profile raw CBOR kinds used before application validation.
#[derive(Clone, Debug, Eq, PartialEq)]
pub enum RawKind {
    /// Basic unsigned-integer argument.
    Unsigned(u64),
    /// Basic negative-integer argument `n`, representing `-1-n`.
    NegativeArgument(u64),
    /// Payload byte range for a definite byte string.
    Bytes(Range<usize>),
    /// Payload byte range for a definite, valid UTF-8 text string.
    Text(Range<usize>),
    /// Payload ranges for an indefinite byte string's definite chunks.
    IndefiniteBytes(Vec<Range<usize>>),
    /// Payload ranges for an indefinite text string's definite chunks.
    IndefiniteText(Vec<Range<usize>>),
    /// Ordered definite array items.
    Array(Vec<RawNode>),
    /// Ordered definite map entries; no key is overwritten.
    Map(Vec<RawMapEntry>),
    /// Numeric tag and losslessly parsed tagged item.
    Tag(u64, Box<RawNode>),
    /// Half-precision float bits.
    Float16(u16),
    /// Single-precision float bits.
    Float32(u32),
    /// Double-precision float bits.
    Float64(u64),
    /// Unsupported simple value.
    Simple(u8),
    /// Boolean.
    Boolean(bool),
    /// Null.
    Null,
}

/// Owned input plus one raw root node. Source spans remain stable.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct RawDocument {
    source: Vec<u8>,
    /// Root node.
    pub root: RawNode,
}

impl RawDocument {
    /// Return the immutable source bytes referenced by every raw span.
    #[must_use]
    pub fn source(&self) -> &[u8] {
        &self.source
    }

    /// Return the exact encoded bytes for a node.
    #[must_use]
    pub fn encoded<'a>(&'a self, node: &RawNode) -> &'a [u8] {
        &self.source[node.span.clone()]
    }
}

struct Parser<'a> {
    input: &'a [u8],
    offset: usize,
    limits: &'a Limits,
    items_seen: usize,
}

impl Parser<'_> {
    fn at_break(&self) -> bool {
        self.input.get(self.offset) == Some(&0xff)
    }

    fn finish_break(&mut self) {
        self.offset += 1;
    }

    fn parse_indefinite_string(&mut self, major: u8, start: usize) -> Result<RawKind, Failure> {
        let mut chunks = Vec::new();
        let mut total_bytes = 0_usize;
        loop {
            if self.at_break() {
                self.finish_break();
                break;
            }
            let chunk_start = self.offset;
            let initial = self.read_u8()?;
            if initial >> 5 != major || initial & 0x1f == 31 {
                return Err(Failure::new(
                    ResultClass::WellFormedness,
                    "wellformed.indefinite_chunk_type",
                    chunk_start,
                ));
            }
            let (length, _) = self.argument(initial & 0x1f, "LENGTH")?;
            let limit = if major == 2 {
                self.limits.max_byte_string_bytes
            } else {
                self.limits.max_text_string_bytes
            };
            if length > limit as u64 {
                return Err(Failure::new(
                    ResultClass::ResourceLimit,
                    "resource.string_bytes",
                    start,
                ));
            }
            let length = usize::try_from(length).map_err(|_| {
                Failure::new(ResultClass::ResourceLimit, "resource.string_bytes", start)
            })?;
            total_bytes = total_bytes.checked_add(length).ok_or_else(|| {
                Failure::new(ResultClass::ResourceLimit, "resource.string_bytes", start)
            })?;
            if total_bytes > limit {
                return Err(Failure::new(
                    ResultClass::ResourceLimit,
                    "resource.string_bytes",
                    start,
                ));
            }
            let payload_start = self.offset;
            let payload_end = payload_start.checked_add(length).ok_or_else(|| {
                Failure::new(
                    ResultClass::WellFormedness,
                    "wellformed.truncated",
                    chunk_start,
                )
            })?;
            let _payload = self.input.get(payload_start..payload_end).ok_or_else(|| {
                Failure::new(
                    ResultClass::WellFormedness,
                    "wellformed.truncated",
                    self.offset,
                )
            })?;
            self.offset = payload_end;
            chunks.push(payload_start..payload_end);
        }
        Ok(if major == 2 {
            RawKind::IndefiniteBytes(chunks)
        } else {
            RawKind::IndefiniteText(chunks)
        })
    }

    #[allow(clippy::too_many_lines)]
    fn parse_node(&mut self, depth: usize) -> Result<RawNode, Failure> {
        self.items_seen = self.items_seen.checked_add(1).ok_or_else(|| {
            Failure::new(
                ResultClass::ResourceLimit,
                "resource.total_items",
                self.offset,
            )
        })?;
        if self.items_seen > self.limits.max_total_items {
            return Err(Failure::new(
                ResultClass::ResourceLimit,
                "resource.total_items",
                self.offset,
            ));
        }
        if depth > self.limits.max_nesting_depth {
            return Err(Failure::new(
                ResultClass::ResourceLimit,
                "resource.depth",
                self.offset,
            ));
        }
        let start = self.offset;
        let initial = self.read_u8()?;
        let major = initial >> 5;
        let additional = initial & 0x1f;
        let (head_form, kind) = match major {
            0 => {
                let (argument, preferred) = self.argument(additional, "INTEGER")?;
                (preferred, RawKind::Unsigned(argument))
            }
            1 => {
                let (argument, preferred) = self.argument(additional, "INTEGER")?;
                (preferred, RawKind::NegativeArgument(argument))
            }
            2 | 3 => {
                if additional == 31 {
                    (
                        HeadForm::Indefinite,
                        self.parse_indefinite_string(major, start)?,
                    )
                } else {
                    let (length, preferred) = self.argument(additional, "LENGTH")?;
                    let limit = if major == 2 {
                        self.limits.max_byte_string_bytes
                    } else {
                        self.limits.max_text_string_bytes
                    };
                    if length > limit as u64 {
                        return Err(Failure::new(
                            ResultClass::ResourceLimit,
                            "resource.string_bytes",
                            start,
                        ));
                    }
                    let length = usize::try_from(length).map_err(|_| {
                        Failure::new(ResultClass::ResourceLimit, "resource.string_bytes", start)
                    })?;
                    let payload_start = self.offset;
                    let payload_end = payload_start.checked_add(length).ok_or_else(|| {
                        Failure::new(ResultClass::WellFormedness, "wellformed.truncated", start)
                    })?;
                    let _payload = self.input.get(payload_start..payload_end).ok_or_else(|| {
                        Failure::new(
                            ResultClass::WellFormedness,
                            "wellformed.truncated",
                            self.offset,
                        )
                    })?;
                    self.offset = payload_end;
                    let range = payload_start..payload_end;
                    let kind = if major == 2 {
                        RawKind::Bytes(range)
                    } else {
                        RawKind::Text(range)
                    };
                    (preferred, kind)
                }
            }
            4 => {
                if additional == 31 {
                    if depth >= self.limits.max_nesting_depth {
                        return Err(Failure::new(
                            ResultClass::ResourceLimit,
                            "resource.depth",
                            start,
                        ));
                    }
                    let mut items = Vec::new();
                    loop {
                        if self.at_break() {
                            self.finish_break();
                            break;
                        }
                        if items.len() >= self.limits.max_array_items {
                            return Err(Failure::new(
                                ResultClass::ResourceLimit,
                                "resource.array_items",
                                start,
                            ));
                        }
                        items.push(self.parse_node(depth + 1)?);
                    }
                    (HeadForm::Indefinite, RawKind::Array(items))
                } else {
                    let (length, preferred) = self.argument(additional, "LENGTH")?;
                    if length > self.limits.max_array_items as u64 {
                        return Err(Failure::new(
                            ResultClass::ResourceLimit,
                            "resource.array_items",
                            start,
                        ));
                    }
                    let length = usize::try_from(length).map_err(|_| {
                        Failure::new(ResultClass::ResourceLimit, "resource.array_items", start)
                    })?;
                    if depth >= self.limits.max_nesting_depth {
                        return Err(Failure::new(
                            ResultClass::ResourceLimit,
                            "resource.depth",
                            start,
                        ));
                    }
                    let mut items = Vec::new();
                    for _ in 0..length {
                        items.push(self.parse_node(depth + 1)?);
                    }
                    (preferred, RawKind::Array(items))
                }
            }
            5 => {
                if additional == 31 {
                    if depth >= self.limits.max_nesting_depth {
                        return Err(Failure::new(
                            ResultClass::ResourceLimit,
                            "resource.depth",
                            start,
                        ));
                    }
                    let mut entries = Vec::new();
                    loop {
                        if self.at_break() {
                            self.finish_break();
                            break;
                        }
                        if entries.len() >= self.limits.max_map_entries {
                            return Err(Failure::new(
                                ResultClass::ResourceLimit,
                                "resource.map_entries",
                                start,
                            ));
                        }
                        let key = self.parse_node(depth + 1)?;
                        if self.at_break() || self.offset == self.input.len() {
                            return Err(Failure::new(
                                ResultClass::WellFormedness,
                                "wellformed.map_pair_missing",
                                self.offset,
                            ));
                        }
                        let value = self.parse_node(depth + 1)?;
                        entries.push(RawMapEntry { key, value });
                    }
                    (HeadForm::Indefinite, RawKind::Map(entries))
                } else {
                    let (length, preferred) = self.argument(additional, "LENGTH")?;
                    if length > self.limits.max_map_entries as u64 {
                        return Err(Failure::new(
                            ResultClass::ResourceLimit,
                            "resource.map_entries",
                            start,
                        ));
                    }
                    let length = usize::try_from(length).map_err(|_| {
                        Failure::new(ResultClass::ResourceLimit, "resource.map_entries", start)
                    })?;
                    if depth >= self.limits.max_nesting_depth {
                        return Err(Failure::new(
                            ResultClass::ResourceLimit,
                            "resource.depth",
                            start,
                        ));
                    }
                    let mut entries = Vec::new();
                    for _ in 0..length {
                        let key = self.parse_node(depth + 1)?;
                        let value = self.parse_node(depth + 1).map_err(|failure| {
                            if failure.class == ResultClass::WellFormedness
                                && failure.code == "wellformed.truncated"
                            {
                                Failure::new(
                                    ResultClass::WellFormedness,
                                    "wellformed.map_pair_missing",
                                    failure.offset,
                                )
                            } else {
                                failure
                            }
                        })?;
                        entries.push(RawMapEntry { key, value });
                    }
                    (preferred, RawKind::Map(entries))
                }
            }
            6 => {
                if additional == 31 {
                    return Err(Failure::new(
                        ResultClass::WellFormedness,
                        "wellformed.reserved_additional",
                        start,
                    ));
                }
                if depth >= self.limits.max_nesting_depth {
                    return Err(Failure::new(
                        ResultClass::ResourceLimit,
                        "resource.depth",
                        start,
                    ));
                }
                let (tag, preferred) = self.argument(additional, "TAG")?;
                let item = self.parse_node(depth + 1)?;
                (preferred, RawKind::Tag(tag, Box::new(item)))
            }
            7 => match additional {
                20 => (HeadForm::Preferred, RawKind::Boolean(false)),
                21 => (HeadForm::Preferred, RawKind::Boolean(true)),
                22 => (HeadForm::Preferred, RawKind::Null),
                23 => (HeadForm::Preferred, RawKind::Simple(23)),
                24 => {
                    let simple = self.read_u8()?;
                    if simple < 24 {
                        return Err(Failure::new(
                            ResultClass::DeterministicProfile,
                            "profile.non_preferred_head",
                            start,
                        ));
                    }
                    (HeadForm::Preferred, RawKind::Simple(simple))
                }
                25 => (
                    HeadForm::Preferred,
                    RawKind::Float16(u16::from_be_bytes(self.read_array::<2>()?)),
                ),
                26 => (
                    HeadForm::Preferred,
                    RawKind::Float32(u32::from_be_bytes(self.read_array::<4>()?)),
                ),
                27 => (
                    HeadForm::Preferred,
                    RawKind::Float64(u64::from_be_bytes(self.read_array::<8>()?)),
                ),
                31 => {
                    return Err(Failure::new(
                        ResultClass::WellFormedness,
                        "wellformed.unexpected_break",
                        start,
                    ));
                }
                28..=30 => {
                    return Err(Failure::new(
                        ResultClass::WellFormedness,
                        "wellformed.reserved_additional",
                        start,
                    ));
                }
                simple => (HeadForm::Preferred, RawKind::Simple(simple)),
            },
            _ => unreachable!("CBOR major type is three bits"),
        };
        Ok(RawNode {
            span: start..self.offset,
            head_form,
            kind,
        })
    }

    fn argument(
        &mut self,
        additional: u8,
        subject: &'static str,
    ) -> Result<(u64, HeadForm), Failure> {
        let (argument, minimum) = match additional {
            value @ 0..=23 => (u64::from(value), 0),
            24 => (u64::from(self.read_u8()?), 24),
            25 => (u64::from(u16::from_be_bytes(self.read_array::<2>()?)), 256),
            26 => (
                u64::from(u32::from_be_bytes(self.read_array::<4>()?)),
                65_536,
            ),
            27 => (
                u64::from_be_bytes(self.read_array::<8>()?),
                u64::from(u32::MAX) + 1,
            ),
            28..=31 => {
                return Err(Failure::new(
                    ResultClass::WellFormedness,
                    "wellformed.reserved_additional",
                    self.offset - 1,
                ));
            }
            _ => unreachable!("additional information is five bits"),
        };
        let form = if minimum != 0 && argument < minimum {
            match subject {
                "INTEGER" => HeadForm::NonPreferredInteger,
                "LENGTH" => HeadForm::NonPreferredLength,
                "TAG" => HeadForm::NonPreferredTag,
                _ => unreachable!("internal argument subject"),
            }
        } else {
            HeadForm::Preferred
        };
        Ok((argument, form))
    }

    fn read_u8(&mut self) -> Result<u8, Failure> {
        let byte = self.input.get(self.offset).copied().ok_or_else(|| {
            Failure::new(
                ResultClass::WellFormedness,
                "wellformed.truncated",
                self.offset,
            )
        })?;
        self.offset += 1;
        Ok(byte)
    }

    fn read_array<const N: usize>(&mut self) -> Result<[u8; N], Failure> {
        let end = self.offset.checked_add(N).ok_or_else(|| {
            Failure::new(
                ResultClass::WellFormedness,
                "wellformed.truncated",
                self.offset,
            )
        })?;
        let bytes = self.input.get(self.offset..end).ok_or_else(|| {
            Failure::new(
                ResultClass::WellFormedness,
                "wellformed.truncated",
                self.offset,
            )
        })?;
        let mut output = [0_u8; N];
        output.copy_from_slice(bytes);
        self.offset = end;
        Ok(output)
    }
}

/// Parse one CBOR item into an ordered, pre-lossy raw document.
///
/// Duplicate entries and indefinite heads are intentionally retained here.
/// Resource failures are fail-early; staged validation later distinguishes
/// validity, expectedness, and deterministic-profile failures.
///
/// # Errors
///
/// Returns a stable [`Failure`] for malformed, invalid, non-profile, or
/// resource-bounded input.
pub fn decode_raw(input: &[u8], limits: &Limits) -> Result<RawDocument, Failure> {
    limits.check()?;
    if input.len() > limits.max_input_bytes {
        return Err(Failure::new(
            ResultClass::ResourceLimit,
            "resource.input_bytes",
            0,
        ));
    }
    if input.is_empty() {
        return Err(Failure::new(
            ResultClass::WellFormedness,
            "wellformed.truncated",
            0,
        ));
    }
    let mut parser = Parser {
        input,
        offset: 0,
        limits,
        items_seen: 0,
    };
    let root = parser.parse_node(0)?;
    if parser.offset != input.len() {
        return Err(Failure::new(
            ResultClass::Expectedness,
            "expected.trailing_bytes",
            parser.offset,
        ));
    }
    Ok(RawDocument {
        source: input.to_vec(),
        root,
    })
}

fn raw_key(document: &RawDocument, node: &RawNode) -> Option<Key> {
    match &node.kind {
        RawKind::Unsigned(value) => Some(Key::Integer(i128::from(*value))),
        RawKind::NegativeArgument(argument) => Some(Key::Integer(-1_i128 - i128::from(*argument))),
        RawKind::Text(range) => core::str::from_utf8(&document.source[range.clone()])
            .ok()
            .map(|text| Key::Text(text.to_owned())),
        _ => None,
    }
}

fn validate_cbor_validity(document: &RawDocument, node: &RawNode) -> Result<(), Failure> {
    match &node.kind {
        RawKind::Text(range) => {
            if core::str::from_utf8(&document.source[range.clone()]).is_err() {
                return Err(Failure::new(
                    ResultClass::Validity,
                    "validity.invalid_utf8",
                    range.start,
                ));
            }
        }
        RawKind::IndefiniteText(chunks) => {
            for range in chunks {
                if core::str::from_utf8(&document.source[range.clone()]).is_err() {
                    return Err(Failure::new(
                        ResultClass::Validity,
                        "validity.invalid_utf8",
                        range.start,
                    ));
                }
            }
        }
        RawKind::Array(items) => {
            for item in items {
                validate_cbor_validity(document, item)?;
            }
        }
        RawKind::Map(entries) => {
            for entry in entries {
                validate_cbor_validity(document, &entry.key)?;
                validate_cbor_validity(document, &entry.value)?;
            }
            for (index, left) in entries.iter().enumerate() {
                for right in &entries[index + 1..] {
                    let equivalent =
                        match (raw_key(document, &left.key), raw_key(document, &right.key)) {
                            (Some(left_key), Some(right_key)) => left_key == right_key,
                            _ => false,
                        };
                    if equivalent {
                        return Err(Failure::new(
                            ResultClass::Validity,
                            "validity.map_duplicate",
                            right.key.span.start,
                        ));
                    }
                }
            }
        }
        RawKind::Tag(_, item) => {
            validate_cbor_validity(document, item)?;
        }
        _ => {}
    }
    Ok(())
}

fn validate_expectedness(document: &RawDocument, node: &RawNode) -> Result<(), Failure> {
    match &node.kind {
        RawKind::Array(items) => {
            for item in items {
                validate_expectedness(document, item)?;
            }
        }
        RawKind::Map(entries) => {
            for entry in entries {
                if raw_key(document, &entry.key).is_none() {
                    return Err(Failure::new(
                        ResultClass::Expectedness,
                        "expected.map_key_type",
                        entry.key.span.start,
                    ));
                }
                validate_expectedness(document, &entry.value)?;
            }
        }
        RawKind::Tag(_, item) => validate_expectedness(document, item)?,
        _ => {}
    }
    Ok(())
}

fn compare_encoded_keys(left: &[u8], right: &[u8], order: MapOrder) -> Ordering {
    match order {
        MapOrder::CoreLexicographic => left.cmp(right),
        MapOrder::DiagnosticLengthFirst => {
            left.len().cmp(&right.len()).then_with(|| left.cmp(right))
        }
    }
}

fn validate_deterministic(
    document: &RawDocument,
    node: &RawNode,
    order: MapOrder,
) -> Result<(), Failure> {
    let non_preferred_code = match node.head_form {
        HeadForm::Preferred => None,
        HeadForm::NonPreferredInteger
        | HeadForm::NonPreferredLength
        | HeadForm::NonPreferredTag => Some("profile.non_preferred_head"),
        HeadForm::Indefinite => Some("profile.indefinite"),
    };
    if let Some(code) = non_preferred_code {
        return Err(Failure::new(
            ResultClass::DeterministicProfile,
            code,
            node.span.start,
        ));
    }
    match &node.kind {
        RawKind::Array(items) => {
            for item in items {
                validate_deterministic(document, item, order)?;
            }
        }
        RawKind::Map(entries) => {
            for entry in entries {
                validate_deterministic(document, &entry.key, order)?;
                validate_deterministic(document, &entry.value, order)?;
            }
            for pair in entries.windows(2) {
                let left = document.encoded(&pair[0].key);
                let right = document.encoded(&pair[1].key);
                if compare_encoded_keys(left, right, order) != Ordering::Less {
                    return Err(Failure::new(
                        ResultClass::DeterministicProfile,
                        "profile.map_order",
                        pair[1].key.span.start,
                    ));
                }
            }
        }
        RawKind::Tag(_, item) => {
            validate_deterministic(document, item, order)?;
            return Err(Failure::new(
                ResultClass::DeterministicProfile,
                "profile.tag_forbidden",
                node.span.start,
            ));
        }
        RawKind::Float16(_) | RawKind::Float32(_) | RawKind::Float64(_) => {
            return Err(Failure::new(
                ResultClass::DeterministicProfile,
                "profile.float_forbidden",
                node.span.start,
            ));
        }
        RawKind::Simple(_) => {
            return Err(Failure::new(
                ResultClass::DeterministicProfile,
                "profile.simple_forbidden",
                node.span.start,
            ));
        }
        _ => {}
    }
    Ok(())
}

fn convert_node(document: &RawDocument, node: &RawNode) -> Result<Value, Failure> {
    match &node.kind {
        RawKind::Unsigned(value) => Ok(Value::Integer(i128::from(*value))),
        RawKind::NegativeArgument(argument) => Ok(Value::Integer(-1_i128 - i128::from(*argument))),
        RawKind::Bytes(range) => Ok(Value::Bytes(document.source[range.clone()].to_vec())),
        RawKind::Text(range) => core::str::from_utf8(&document.source[range.clone()])
            .map(|text| Value::Text(text.to_owned()))
            .map_err(|_| Failure::new(ResultClass::Validity, "validity.invalid_utf8", range.start)),
        RawKind::IndefiniteBytes(_) | RawKind::IndefiniteText(_) => Err(Failure::new(
            ResultClass::DeterministicProfile,
            "profile.indefinite",
            node.span.start,
        )),
        RawKind::Array(items) => items
            .iter()
            .map(|item| convert_node(document, item))
            .collect::<Result<Vec<_>, _>>()
            .map(Value::Array),
        RawKind::Map(entries) => {
            let mut output = Vec::new();
            for entry in entries {
                let key = raw_key(document, &entry.key).ok_or_else(|| {
                    Failure::new(
                        ResultClass::Expectedness,
                        "expected.map_key_type",
                        entry.key.span.start,
                    )
                })?;
                output.push(MapEntry {
                    key,
                    value: convert_node(document, &entry.value)?,
                });
            }
            Ok(Value::Map(output))
        }
        RawKind::Tag(_, _) => Err(Failure::new(
            ResultClass::DeterministicProfile,
            "profile.tag_forbidden",
            node.span.start,
        )),
        RawKind::Float16(_) | RawKind::Float32(_) | RawKind::Float64(_) => Err(Failure::new(
            ResultClass::DeterministicProfile,
            "profile.float_forbidden",
            node.span.start,
        )),
        RawKind::Simple(_) => Err(Failure::new(
            ResultClass::DeterministicProfile,
            "profile.simple_forbidden",
            node.span.start,
        )),
        RawKind::Boolean(value) => Ok(Value::Boolean(*value)),
        RawKind::Null => Ok(Value::Null),
    }
}

/// Validate a raw document in explicit stages and return the accepted value.
///
/// Duplicate checks occur while the raw ordered entry sequence is still
/// present. No native map is constructed.
///
/// # Errors
///
/// Returns the first stable staged validation failure.
pub fn validate_raw(document: &RawDocument, profile: &Profile) -> Result<Value, Failure> {
    validate_raw_with_expectations(document, profile, None, None)
}

fn matches_top_level(node: &RawNode, expected: &str) -> bool {
    matches!(
        (expected, &node.kind),
        (
            "integer",
            RawKind::Unsigned(_) | RawKind::NegativeArgument(_)
        ) | ("bytes", RawKind::Bytes(_) | RawKind::IndefiniteBytes(_))
            | ("text", RawKind::Text(_) | RawKind::IndefiniteText(_))
            | ("array", RawKind::Array(_))
            | ("map", RawKind::Map(_))
            | ("boolean", RawKind::Boolean(_))
            | ("null", RawKind::Null)
    )
}

/// Validate a raw document with optional caller expectations.
///
/// Profile and top-level expectations are checked after CBOR validity and
/// application key validity, but before deterministic-profile checks.
///
/// # Errors
///
/// Returns the first stable staged validation failure.
pub fn validate_raw_with_expectations(
    document: &RawDocument,
    profile: &Profile,
    expected_profile_id: Option<&str>,
    expected_top_level: Option<&str>,
) -> Result<Value, Failure> {
    profile.limits.check()?;
    if document.source.len() > profile.limits.max_input_bytes {
        return Err(Failure::new(
            ResultClass::ResourceLimit,
            "resource.input_bytes",
            0,
        ));
    }
    validate_cbor_validity(document, &document.root)?;
    validate_expectedness(document, &document.root)?;
    if expected_profile_id.is_some_and(|identifier| identifier != PROFILE_ID) {
        return Err(Failure::new(
            ResultClass::Expectedness,
            "expected.profile_id",
            0,
        ));
    }
    if expected_top_level.is_some_and(|expected| !matches_top_level(&document.root, expected)) {
        return Err(Failure::new(
            ResultClass::Expectedness,
            "expected.top_level",
            document.root.span.start,
        ));
    }
    validate_deterministic(document, &document.root, profile.map_order)?;
    convert_node(document, &document.root)
}

/// Strictly parse and validate one candidate-profile item.
///
/// # Errors
///
/// Returns a stable parse, validity, expectedness, profile, semantic, or
/// resource failure.
pub fn decode(input: &[u8], profile: &Profile) -> Result<Value, Failure> {
    let document = decode_raw(input, &profile.limits)?;
    validate_raw(&document, profile)
}

#[derive(Debug)]
struct OutputLimit;

#[derive(Debug)]
struct CappedWriter {
    bytes: Vec<u8>,
    limit: usize,
}

impl CappedWriter {
    fn new(limit: usize) -> Self {
        Self {
            bytes: Vec::new(),
            limit,
        }
    }

    fn append(&mut self, bytes: &[u8]) -> Result<(), Failure> {
        self.write_all(bytes)
            .map_err(|_| Failure::new(ResultClass::ResourceLimit, "resource.output_bytes", 0))
    }
}

impl CborWrite for CappedWriter {
    type Error = OutputLimit;

    fn write_all(&mut self, bytes: &[u8]) -> Result<(), Self::Error> {
        let Some(new_length) = self.bytes.len().checked_add(bytes.len()) else {
            return Err(OutputLimit);
        };
        if new_length > self.limit {
            return Err(OutputLimit);
        }
        self.bytes.extend_from_slice(bytes);
        Ok(())
    }
}

fn encoder_failure<E>(_: minicbor::encode::Error<E>) -> Failure {
    Failure::new(ResultClass::ResourceLimit, "resource.output_bytes", 0)
}

fn encode_key(key: &Key, limit: usize) -> Result<Vec<u8>, Failure> {
    let mut writer = CappedWriter::new(limit);
    {
        let mut encoder = Encoder::new(&mut writer);
        match key {
            Key::Integer(value) => {
                encoder.i128(*value).map_err(encoder_failure)?;
            }
            Key::Text(value) => {
                encoder.str(value).map_err(encoder_failure)?;
            }
        }
    }
    Ok(writer.bytes)
}

#[allow(clippy::too_many_lines)]
fn validate_semantic_value(
    value: &Value,
    profile: &Profile,
    depth: usize,
    items_seen: &mut usize,
) -> Result<(), Failure> {
    *items_seen = items_seen
        .checked_add(1)
        .ok_or_else(|| Failure::new(ResultClass::ResourceLimit, "resource.total_items", 0))?;
    if *items_seen > profile.limits.max_total_items {
        return Err(Failure::new(
            ResultClass::ResourceLimit,
            "resource.total_items",
            0,
        ));
    }
    if depth > profile.limits.max_nesting_depth {
        return Err(Failure::new(
            ResultClass::ResourceLimit,
            "resource.depth",
            0,
        ));
    }
    match value {
        Value::Integer(integer) if !(MIN_INTEGER..=MAX_INTEGER).contains(integer) => Err(
            Failure::new(ResultClass::SemanticValidity, "semantic.integer_range", 0),
        ),
        Value::Bytes(bytes) if bytes.len() > profile.limits.max_byte_string_bytes => Err(
            Failure::new(ResultClass::ResourceLimit, "resource.string_bytes", 0),
        ),
        Value::Text(text) if text.len() > profile.limits.max_text_string_bytes => Err(
            Failure::new(ResultClass::ResourceLimit, "resource.string_bytes", 0),
        ),
        Value::Array(items) => {
            if items.len() > profile.limits.max_array_items {
                return Err(Failure::new(
                    ResultClass::ResourceLimit,
                    "resource.array_items",
                    0,
                ));
            }
            if depth >= profile.limits.max_nesting_depth {
                return Err(Failure::new(
                    ResultClass::ResourceLimit,
                    "resource.depth",
                    0,
                ));
            }
            for item in items {
                validate_semantic_value(item, profile, depth + 1, items_seen)?;
            }
            Ok(())
        }
        Value::Map(entries) => {
            if entries.len() > profile.limits.max_map_entries {
                return Err(Failure::new(
                    ResultClass::ResourceLimit,
                    "resource.map_entries",
                    0,
                ));
            }
            if depth >= profile.limits.max_nesting_depth {
                return Err(Failure::new(
                    ResultClass::ResourceLimit,
                    "resource.depth",
                    0,
                ));
            }
            for (index, entry) in entries.iter().enumerate() {
                *items_seen = items_seen.checked_add(1).ok_or_else(|| {
                    Failure::new(ResultClass::ResourceLimit, "resource.total_items", 0)
                })?;
                if *items_seen > profile.limits.max_total_items {
                    return Err(Failure::new(
                        ResultClass::ResourceLimit,
                        "resource.total_items",
                        0,
                    ));
                }
                match &entry.key {
                    Key::Integer(integer) if !(MIN_INTEGER..=MAX_INTEGER).contains(integer) => {
                        return Err(Failure::new(
                            ResultClass::SemanticValidity,
                            "semantic.integer_range",
                            0,
                        ));
                    }
                    Key::Text(text) if text.len() > profile.limits.max_text_string_bytes => {
                        return Err(Failure::new(
                            ResultClass::ResourceLimit,
                            "resource.string_bytes",
                            0,
                        ));
                    }
                    _ => {}
                }
                if entries[index + 1..]
                    .iter()
                    .any(|other| entry.key == other.key)
                {
                    return Err(Failure::new(
                        ResultClass::SemanticValidity,
                        "semantic.map_duplicate",
                        0,
                    ));
                }
                validate_semantic_value(&entry.value, profile, depth + 1, items_seen)?;
            }
            Ok(())
        }
        _ => Ok(()),
    }
}

fn encode_into(value: &Value, profile: &Profile, writer: &mut CappedWriter) -> Result<(), Failure> {
    match value {
        Value::Integer(value) => {
            Encoder::new(writer).i128(*value).map_err(encoder_failure)?;
            Ok(())
        }
        Value::Bytes(value) => {
            Encoder::new(writer).bytes(value).map_err(encoder_failure)?;
            Ok(())
        }
        Value::Text(value) => {
            Encoder::new(writer).str(value).map_err(encoder_failure)?;
            Ok(())
        }
        Value::Boolean(value) => {
            Encoder::new(writer).bool(*value).map_err(encoder_failure)?;
            Ok(())
        }
        Value::Null => {
            Encoder::new(writer).null().map_err(encoder_failure)?;
            Ok(())
        }
        Value::Array(items) => {
            Encoder::new(&mut *writer)
                .array(items.len() as u64)
                .map_err(encoder_failure)?;
            for item in items {
                encode_into(item, profile, writer)?;
            }
            Ok(())
        }
        Value::Map(entries) => {
            let mut ordered = Vec::new();
            for (index, entry) in entries.iter().enumerate() {
                ordered.push((
                    index,
                    encode_key(&entry.key, profile.limits.max_output_bytes)?,
                ));
            }
            ordered
                .sort_by(|left, right| compare_encoded_keys(&left.1, &right.1, profile.map_order));
            Encoder::new(&mut *writer)
                .map(entries.len() as u64)
                .map_err(encoder_failure)?;
            for (index, key_bytes) in ordered {
                writer.append(&key_bytes)?;
                encode_into(&entries[index].value, profile, writer)?;
            }
            Ok(())
        }
    }
}

/// Encode a semantic value through the bounded `minicbor` primitive path.
///
/// Map ordering, duplicate behavior, supported types, and limits are enforced
/// by this crate rather than delegated to `minicbor` native maps or values.
///
/// # Errors
///
/// Returns a stable semantic or resource failure.
pub fn encode(value: &Value, profile: &Profile) -> Result<Vec<u8>, Failure> {
    profile.limits.check()?;
    let mut items_seen = 0;
    validate_semantic_value(value, profile, 0, &mut items_seen)?;
    let mut writer = CappedWriter::new(profile.limits.max_output_bytes);
    encode_into(value, profile, &mut writer)?;
    Ok(writer.bytes)
}

/// Identifiers bound by the generic data-free framing experiment.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct FrameIdentifiers<'a> {
    /// Test-only digest purpose, such as `test-manifest`.
    pub purpose: &'a str,
    /// Algorithm identifier; only [`SHA256_ALGORITHM_ID`] is accepted.
    pub algorithm_id: &'a str,
    /// Encoding profile identifier.
    pub profile_id: &'a str,
    /// Test-only data-free object-class identifier.
    pub object_class_schema_id: &'a str,
    /// Framing identifier.
    pub framing_id: &'a str,
}

impl<'a> FrameIdentifiers<'a> {
    /// Construct identifiers for the sole implemented SHA-256 framing path.
    #[must_use]
    pub const fn sha256(purpose: &'a str, object_class_schema_id: &'a str) -> Self {
        Self {
            purpose,
            algorithm_id: SHA256_ALGORITHM_ID,
            profile_id: PROFILE_ID,
            object_class_schema_id,
            framing_id: FRAMING_ID,
        }
    }
}

fn check_frame_identifier(identifier: &str, code: &'static str) -> Result<(), Failure> {
    let bytes = identifier.as_bytes();
    let first_valid = bytes
        .first()
        .is_some_and(|byte| byte.is_ascii_lowercase() || byte.is_ascii_digit());
    let rest_valid = bytes.iter().skip(1).all(|byte| {
        byte.is_ascii_lowercase()
            || byte.is_ascii_digit()
            || matches!(byte, b'.' | b'_' | b':' | b'-')
    });
    if bytes.len() > 128 || !first_valid || !rest_valid {
        Err(Failure::new(ResultClass::DigestVerification, code, 0))
    } else {
        Ok(())
    }
}

/// Build fixed-magic, six-component, u32-be length-delimited data-free bytes.
///
/// The six components are purpose, algorithm, profile, object class, framing
/// identifier, and canonical payload. The payload is strictly revalidated
/// under the fixed core profile. The object-class/schema identifier is bound
/// exactly but is not resolved or checked for schema conformance. This does not
/// define a logical-data digest or a production digest domain.
///
/// # Errors
///
/// Returns a stable identifier, algorithm, length, or output-limit failure.
pub fn frame_data_free(
    identifiers: &FrameIdentifiers<'_>,
    canonical_payload: &[u8],
    limits: &Limits,
) -> Result<Vec<u8>, Failure> {
    limits.check()?;
    if identifiers.algorithm_id != SHA256_ALGORITHM_ID {
        return Err(Failure::new(
            ResultClass::DigestVerification,
            "digest.algorithm",
            0,
        ));
    }
    if identifiers.profile_id != PROFILE_ID {
        return Err(Failure::new(
            ResultClass::DigestVerification,
            "digest.profile",
            0,
        ));
    }
    if identifiers.framing_id != FRAMING_ID {
        return Err(Failure::new(
            ResultClass::DigestVerification,
            "digest.framing",
            0,
        ));
    }
    check_frame_identifier(identifiers.purpose, "digest.purpose")?;
    check_frame_identifier(identifiers.algorithm_id, "digest.algorithm")?;
    check_frame_identifier(identifiers.profile_id, "digest.profile")?;
    check_frame_identifier(
        identifiers.object_class_schema_id,
        "digest.object_class_schema",
    )?;
    check_frame_identifier(identifiers.framing_id, "digest.framing")?;
    if canonical_payload.is_empty() {
        return Err(Failure::new(
            ResultClass::DigestVerification,
            "digest.payload",
            0,
        ));
    }
    if canonical_payload.len() > limits.max_output_bytes {
        return Err(Failure::new(
            ResultClass::DigestVerification,
            "digest.length",
            0,
        ));
    }
    let framing_profile = Profile {
        limits: limits.clone(),
        map_order: MapOrder::CoreLexicographic,
    };
    decode(canonical_payload, &framing_profile)
        .map_err(|_| Failure::new(ResultClass::DigestVerification, "digest.payload", 0))?;
    let components = [
        identifiers.purpose.as_bytes(),
        identifiers.algorithm_id.as_bytes(),
        identifiers.profile_id.as_bytes(),
        identifiers.object_class_schema_id.as_bytes(),
        identifiers.framing_id.as_bytes(),
        canonical_payload,
    ];
    let mut total = FRAME_MAGIC.len();
    for component in components {
        u32::try_from(component.len()).map_err(|_| {
            Failure::new(
                ResultClass::DigestVerification,
                "digest.component_length",
                0,
            )
        })?;
        total = total
            .checked_add(4)
            .and_then(|value| value.checked_add(component.len()))
            .ok_or_else(|| Failure::new(ResultClass::DigestVerification, "digest.length", 0))?;
    }
    if total > limits.max_digest_frame_bytes {
        return Err(Failure::new(
            ResultClass::DigestVerification,
            "digest.length",
            0,
        ));
    }
    let mut framed = Vec::with_capacity(total);
    framed.extend_from_slice(FRAME_MAGIC);
    for component in components {
        let length = u32::try_from(component.len()).map_err(|_| {
            Failure::new(
                ResultClass::DigestVerification,
                "digest.component_length",
                0,
            )
        })?;
        framed.extend_from_slice(&length.to_be_bytes());
        framed.extend_from_slice(component);
    }
    Ok(framed)
}

/// SHA-256 digest of [`frame_data_free`] bytes.
///
/// # Errors
///
/// Returns any stable failure produced while building the framed bytes.
pub fn digest_data_free(
    identifiers: &FrameIdentifiers<'_>,
    canonical_payload: &[u8],
    limits: &Limits,
) -> Result<[u8; 32], Failure> {
    let framed = frame_data_free(identifiers, canonical_payload, limits)?;
    Ok(Sha256::digest(framed).into())
}

/// Payload and semantic value returned by successful digest verification.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct VerifiedFrame {
    /// Exact accepted canonical payload bytes.
    pub payload: Vec<u8>,
    /// Semantic value decoded from the payload.
    pub value: Value,
}

fn digest_failure(code: &'static str, offset: usize) -> Failure {
    Failure::new(ResultClass::DigestVerification, code, offset)
}

fn framed_identifier<'a>(
    bytes: &'a [u8],
    expected: &str,
    code: &'static str,
) -> Result<&'a str, Failure> {
    let actual = core::str::from_utf8(bytes).map_err(|_| digest_failure(code, 0))?;
    check_frame_identifier(actual, code)?;
    if actual == expected {
        Ok(actual)
    } else {
        Err(digest_failure(code, 0))
    }
}

/// Verify one complete data-free frame and exact 32-byte SHA-256 digest.
///
/// The caller supplies every expected domain identifier. The framed payload is
/// revalidated as exact candidate-profile bytes before digest comparison.
///
/// # Errors
///
/// Returns a stable `digest.*` failure according to candidate precedence.
pub fn verify_digest_data_free(
    expected: &FrameIdentifiers<'_>,
    framed: &[u8],
    supplied_digest: &[u8],
    profile: &Profile,
) -> Result<VerifiedFrame, Failure> {
    profile.limits.check()?;
    if framed.len() > profile.limits.max_digest_frame_bytes || supplied_digest.len() != 32 {
        return Err(digest_failure("digest.length", 0));
    }
    if !framed.starts_with(FRAME_MAGIC) {
        return Err(digest_failure("digest.magic", 0));
    }

    let mut offset = FRAME_MAGIC.len();
    let mut components: Vec<&[u8]> = Vec::with_capacity(6);
    for index in 0..6 {
        let prefix = framed
            .get(offset..offset.saturating_add(4))
            .ok_or_else(|| digest_failure("digest.component_length", offset))?;
        let length = usize::try_from(u32::from_be_bytes(
            prefix
                .try_into()
                .map_err(|_| digest_failure("digest.component_length", offset))?,
        ))
        .map_err(|_| digest_failure("digest.component_length", offset))?;
        offset += 4;
        if index == 5 && length > profile.limits.max_output_bytes {
            return Err(digest_failure("digest.length", offset - 4));
        }
        let end = offset
            .checked_add(length)
            .ok_or_else(|| digest_failure("digest.component_length", offset))?;
        let component = framed
            .get(offset..end)
            .ok_or_else(|| digest_failure("digest.component_length", offset))?;
        components.push(component);
        offset = end;
    }
    if offset != framed.len() {
        return Err(digest_failure("digest.trailing_bytes", offset));
    }

    check_frame_identifier(expected.purpose, "digest.purpose")?;
    check_frame_identifier(expected.algorithm_id, "digest.algorithm")?;
    check_frame_identifier(expected.profile_id, "digest.profile")?;
    check_frame_identifier(
        expected.object_class_schema_id,
        "digest.object_class_schema",
    )?;
    check_frame_identifier(expected.framing_id, "digest.framing")?;
    if expected.algorithm_id != SHA256_ALGORITHM_ID {
        return Err(digest_failure("digest.algorithm", 0));
    }
    if expected.profile_id != PROFILE_ID {
        return Err(digest_failure("digest.profile", 0));
    }
    if expected.framing_id != FRAMING_ID {
        return Err(digest_failure("digest.framing", 0));
    }

    framed_identifier(components[0], expected.purpose, "digest.purpose")?;
    framed_identifier(components[1], expected.algorithm_id, "digest.algorithm")?;
    framed_identifier(components[2], expected.profile_id, "digest.profile")?;
    framed_identifier(
        components[3],
        expected.object_class_schema_id,
        "digest.object_class_schema",
    )?;
    framed_identifier(components[4], expected.framing_id, "digest.framing")?;

    let payload = components[5];
    if payload.is_empty() {
        return Err(digest_failure("digest.payload", 0));
    }
    let value = decode(payload, profile).map_err(|_| digest_failure("digest.payload", 0))?;
    let rebuilt = frame_data_free(expected, payload, &profile.limits)?;
    if rebuilt != framed {
        return Err(digest_failure("digest.payload", 0));
    }
    let calculated: [u8; 32] = Sha256::digest(framed).into();
    if calculated.as_slice() != supplied_digest {
        return Err(digest_failure("digest.mismatch", 0));
    }
    Ok(VerifiedFrame {
        payload: payload.to_vec(),
        value,
    })
}

fn diagnostic_failure(_: &'static str) -> Failure {
    Failure::new(ResultClass::Expectedness, "expected.top_level", 0)
}

fn semantic_failure(code: &'static str) -> Failure {
    Failure::new(ResultClass::SemanticValidity, code, 0)
}

fn exact_fields(object: &JsonMap<String, JsonValue>, fields: &[&str]) -> bool {
    object.len() == fields.len() && fields.iter().all(|field| object.contains_key(*field))
}

fn discriminator(object: &JsonMap<String, JsonValue>) -> Option<(&str, &str)> {
    if let Some(kind) = object.get("type").and_then(JsonValue::as_str) {
        Some(("type", kind))
    } else {
        object
            .get("kind")
            .and_then(JsonValue::as_str)
            .map(|kind| ("kind", kind))
    }
}

fn parse_integer_text(value: &JsonValue) -> Result<i128, Failure> {
    let integer = value
        .as_str()
        .ok_or_else(|| diagnostic_failure("INTEGER_MUST_BE_DECIMAL_STRING"))?
        .parse::<i128>()
        .map_err(|_| diagnostic_failure("INTEGER_DECIMAL_INVALID"))?;
    if (MIN_INTEGER..=MAX_INTEGER).contains(&integer) {
        Ok(integer)
    } else {
        Err(Failure::new(
            ResultClass::SemanticValidity,
            "semantic.integer_range",
            0,
        ))
    }
}

fn parse_exact_i128(value: &JsonValue) -> Result<i128, Failure> {
    value
        .as_str()
        .ok_or_else(|| diagnostic_failure("DECIMAL_STRING_REQUIRED"))?
        .parse::<i128>()
        .map_err(|_| diagnostic_failure("DECIMAL_STRING_INVALID"))
}

fn is_decimal_integer(value: &JsonValue) -> bool {
    let Some(value) = value.as_str() else {
        return false;
    };
    let digits = value.strip_prefix('-').unwrap_or(value);
    !digits.is_empty()
        && digits.bytes().all(|byte| byte.is_ascii_digit())
        && (digits == "0" || !digits.starts_with('0'))
        && value != "-0"
}

fn gcd(mut left: u128, mut right: u128) -> u128 {
    while right != 0 {
        let remainder = left % right;
        left = right;
        right = remainder;
    }
    left
}

fn unsupported_bignum(object: &JsonMap<String, JsonValue>) -> Result<Value, Failure> {
    let (discriminator, decimal_field) = if object.contains_key("type") {
        ("type", "value")
    } else {
        ("kind", "decimal")
    };
    if !exact_fields(object, &[discriminator, decimal_field])
        || !is_decimal_integer(&object[decimal_field])
    {
        return Err(diagnostic_failure("BIGNUM_INVALID"));
    }
    Err(semantic_failure("semantic.unsupported_bignum"))
}

fn unsupported_rational(object: &JsonMap<String, JsonValue>) -> Result<Value, Failure> {
    let discriminator = if object.contains_key("type") {
        "type"
    } else {
        "kind"
    };
    if !exact_fields(object, &[discriminator, "numerator", "denominator"]) {
        return Err(diagnostic_failure("RATIONAL_INVALID"));
    }
    let numerator = parse_exact_i128(&object["numerator"])?;
    let denominator = parse_exact_i128(&object["denominator"])?;
    if denominator <= 0 || gcd(numerator.unsigned_abs(), denominator.unsigned_abs()) != 1 {
        Err(semantic_failure("semantic.rational_invalid"))
    } else {
        Err(semantic_failure("semantic.unsupported_rational"))
    }
}

fn unsupported_decimal(object: &JsonMap<String, JsonValue>) -> Result<Value, Failure> {
    let discriminator = if object.contains_key("type") {
        "type"
    } else {
        "kind"
    };
    if !exact_fields(object, &[discriminator, "coefficient", "exponent"]) {
        return Err(diagnostic_failure("DECIMAL_INVALID"));
    }
    let coefficient = parse_exact_i128(&object["coefficient"])?;
    let exponent = parse_exact_i128(&object["exponent"])?;
    if (coefficient == 0 && exponent != 0) || (coefficient != 0 && coefficient % 10 == 0) {
        Err(semantic_failure("semantic.decimal_non_normal"))
    } else {
        Err(semantic_failure("semantic.unsupported_decimal"))
    }
}

fn unsupported_ieee_bits(object: &JsonMap<String, JsonValue>) -> Result<Value, Failure> {
    let discriminator = if object.contains_key("type") {
        "type"
    } else {
        "kind"
    };
    if !exact_fields(object, &[discriminator, "width", "bits_hex"]) {
        return Err(diagnostic_failure("IEEE_BITS_INVALID"));
    }
    let width = object["width"]
        .as_u64()
        .ok_or_else(|| diagnostic_failure("IEEE_WIDTH_INVALID"))?;
    let bits = object["bits_hex"]
        .as_str()
        .ok_or_else(|| diagnostic_failure("IEEE_BITS_INVALID"))?;
    let expected_hex_digits = match width {
        16 => 4,
        32 => 8,
        64 => 16,
        _ => return Err(diagnostic_failure("IEEE_WIDTH_INVALID")),
    };
    if bits.len() != expected_hex_digits || hex_decode(bits).is_err() {
        return Err(diagnostic_failure("IEEE_BITS_INVALID"));
    }
    Err(semantic_failure("semantic.unsupported_ieee_bits"))
}

fn interval_integer_bounds(object: &JsonMap<String, JsonValue>) -> Result<bool, Failure> {
    let lower = parse_exact_i128(&object["lower"])
        .map_err(|_| semantic_failure("semantic.interval_invalid"))?;
    let upper = parse_exact_i128(&object["upper"])
        .map_err(|_| semantic_failure("semantic.interval_invalid"))?;
    Ok(lower <= upper)
}

fn unsupported_interval(object: &JsonMap<String, JsonValue>) -> Result<Value, Failure> {
    let discriminator = if object.contains_key("type") {
        "type"
    } else {
        "kind"
    };
    let closure_valid = object
        .get("closure")
        .and_then(JsonValue::as_str)
        .is_some_and(|closure| matches!(closure, "open" | "closed" | "left_open" | "right_open"));
    if !closure_valid {
        return Err(semantic_failure("semantic.interval_invalid"));
    }
    if exact_fields(
        object,
        &[discriminator, "endpoint_kind", "lower", "upper", "closure"],
    ) {
        let ordered = match object["endpoint_kind"].as_str() {
            Some("integer") => interval_integer_bounds(object)?,
            Some("rational" | "decimal") => true,
            _ => false,
        };
        return if ordered {
            Err(semantic_failure("semantic.unsupported_interval"))
        } else {
            Err(semantic_failure("semantic.interval_invalid"))
        };
    }
    if !exact_fields(object, &[discriminator, "lower", "upper", "closure"]) {
        return Err(semantic_failure("semantic.interval_invalid"));
    }
    let lower = object["lower"]
        .as_object()
        .ok_or_else(|| semantic_failure("semantic.interval_invalid"))?;
    let upper = object["upper"]
        .as_object()
        .ok_or_else(|| semantic_failure("semantic.interval_invalid"))?;
    let lower_kind = lower.get("type").or_else(|| lower.get("kind"));
    let upper_kind = upper.get("type").or_else(|| upper.get("kind"));
    let lower_kind = lower_kind.and_then(JsonValue::as_str);
    if lower_kind != upper_kind.and_then(JsonValue::as_str) {
        return Err(semantic_failure("semantic.interval_invalid"));
    }
    if lower_kind == Some("integer") {
        let lower_value = lower
            .get("value")
            .or_else(|| lower.get("decimal"))
            .ok_or_else(|| semantic_failure("semantic.interval_invalid"))?;
        let upper_value = upper
            .get("value")
            .or_else(|| upper.get("decimal"))
            .ok_or_else(|| semantic_failure("semantic.interval_invalid"))?;
        let lower_value = parse_exact_i128(lower_value)
            .map_err(|_| semantic_failure("semantic.interval_invalid"))?;
        let upper_value = parse_exact_i128(upper_value)
            .map_err(|_| semantic_failure("semantic.interval_invalid"))?;
        if lower_value > upper_value {
            return Err(semantic_failure("semantic.interval_invalid"));
        }
    }
    Err(semantic_failure("semantic.unsupported_interval"))
}

fn classify_extensions(extensions: &JsonValue) -> Result<Value, Failure> {
    let extensions = extensions
        .as_array()
        .ok_or_else(|| diagnostic_failure("EXTENSIONS_INVALID"))?;
    let mut type_ids: Vec<&str> = Vec::with_capacity(extensions.len());
    let mut any_critical = false;
    for extension in extensions {
        let extension = extension
            .as_object()
            .ok_or_else(|| diagnostic_failure("EXTENSION_INVALID"))?;
        let bare = exact_fields(extension, &["type_id", "critical", "body"]);
        let typed = exact_fields(extension, &["type", "type_id", "critical", "body"])
            && extension.get("type").and_then(JsonValue::as_str) == Some("extension");
        if !bare && !typed {
            return Err(diagnostic_failure("EXTENSION_INVALID"));
        }
        let type_id = extension["type_id"]
            .as_str()
            .ok_or_else(|| diagnostic_failure("EXTENSION_INVALID"))?;
        let critical = extension["critical"]
            .as_bool()
            .ok_or_else(|| diagnostic_failure("EXTENSION_INVALID"))?;
        if type_ids.contains(&type_id) {
            return Err(semantic_failure("semantic.extension_duplicate"));
        }
        type_ids.push(type_id);
        any_critical |= critical;
    }
    if any_critical {
        Err(semantic_failure("semantic.extension_critical_unknown"))
    } else {
        Err(semantic_failure(
            "semantic.extension_noncritical_unsupported",
        ))
    }
}

fn unsupported_extension(object: &JsonMap<String, JsonValue>) -> Result<Value, Failure> {
    let discriminator = if object.contains_key("type") {
        "type"
    } else {
        "kind"
    };
    if !exact_fields(object, &[discriminator, "type_id", "critical", "body"]) {
        return Err(diagnostic_failure("EXTENSION_INVALID"));
    }
    let mut extension = JsonMap::new();
    for field in ["type_id", "critical", "body"] {
        extension.insert(field.to_owned(), object[field].clone());
    }
    classify_extensions(&JsonValue::Array(vec![JsonValue::Object(extension)]))
}

fn parse_diagnostic_key(value: &JsonValue) -> Result<Key, Failure> {
    let object = value
        .as_object()
        .ok_or_else(|| diagnostic_failure("KEY_MUST_BE_OBJECT"))?;
    let kind = object
        .get("type")
        .and_then(JsonValue::as_str)
        .ok_or_else(|| diagnostic_failure("TYPE_MISSING"))?;
    match kind {
        "integer" if exact_fields(object, &["type", "value"]) => {
            parse_integer_text(&object["value"]).map(Key::Integer)
        }
        "text" if exact_fields(object, &["type", "value"]) => object["value"]
            .as_str()
            .map(|text| Key::Text(text.to_owned()))
            .ok_or_else(|| diagnostic_failure("TEXT_VALUE_INVALID")),
        "integer" | "text" => Err(diagnostic_failure("UNKNOWN_OR_MISSING_FIELD")),
        "bytes" | "boolean" | "null" | "array" | "map" | "bignum" | "rational" | "decimal"
        | "ieee_bits" | "interval" | "extension" | "extension_sequence" => {
            Err(semantic_failure("semantic.map_key_type"))
        }
        _ => Err(diagnostic_failure("MAP_KEY_TYPE_UNSUPPORTED")),
    }
}

fn parse_diagnostic_value(value: &JsonValue) -> Result<Value, Failure> {
    let object = value
        .as_object()
        .ok_or_else(|| diagnostic_failure("VALUE_MUST_BE_OBJECT"))?;
    let (discriminator, kind) =
        discriminator(object).ok_or_else(|| diagnostic_failure("TYPE_MISSING"))?;
    match kind {
        "integer" if exact_fields(object, &["type", "value"]) => {
            parse_integer_text(&object["value"]).map(Value::Integer)
        }
        "bytes" if exact_fields(object, &["type", "hex"]) => object["hex"]
            .as_str()
            .ok_or_else(|| diagnostic_failure("BYTES_HEX_INVALID"))
            .and_then(hex_decode)
            .map(Value::Bytes),
        "text" if exact_fields(object, &["type", "value"]) => object["value"]
            .as_str()
            .map(|text| Value::Text(text.to_owned()))
            .ok_or_else(|| diagnostic_failure("TEXT_VALUE_INVALID")),
        "array" if exact_fields(object, &["type", "items"]) => object["items"]
            .as_array()
            .ok_or_else(|| diagnostic_failure("ARRAY_ITEMS_INVALID"))?
            .iter()
            .map(parse_diagnostic_value)
            .collect::<Result<Vec<_>, _>>()
            .map(Value::Array),
        "map" if exact_fields(object, &["type", "entries"]) => {
            let entries = object["entries"]
                .as_array()
                .ok_or_else(|| diagnostic_failure("MAP_ENTRIES_INVALID"))?;
            let mut output = Vec::new();
            for entry in entries {
                let entry = entry
                    .as_object()
                    .ok_or_else(|| diagnostic_failure("MAP_ENTRY_INVALID"))?;
                if !exact_fields(entry, &["key", "value"]) {
                    return Err(diagnostic_failure("UNKNOWN_OR_MISSING_FIELD"));
                }
                output.push(MapEntry {
                    key: parse_diagnostic_key(&entry["key"])?,
                    value: parse_diagnostic_value(&entry["value"])?,
                });
            }
            Ok(Value::Map(output))
        }
        "boolean" if exact_fields(object, &["type", "value"]) => object["value"]
            .as_bool()
            .map(Value::Boolean)
            .ok_or_else(|| diagnostic_failure("BOOLEAN_VALUE_INVALID")),
        "null" if exact_fields(object, &["type"]) => Ok(Value::Null),
        "bignum" => unsupported_bignum(object),
        "rational" => unsupported_rational(object),
        "decimal" => unsupported_decimal(object),
        "ieee_bits" => unsupported_ieee_bits(object),
        "interval" => unsupported_interval(object),
        "extension" => unsupported_extension(object),
        "extension_sequence" if exact_fields(object, &[discriminator, "extensions"]) => {
            classify_extensions(&object["extensions"])
        }
        "integer" | "bytes" | "text" | "array" | "map" | "boolean" | "null" => {
            Err(diagnostic_failure("UNKNOWN_OR_MISSING_FIELD"))
        }
        _ => Err(diagnostic_failure("TYPE_UNSUPPORTED")),
    }
}

/// Parse the non-normative typed JSON projection.
///
/// # Errors
///
/// Returns stable expectedness or semantic failures for malformed,
/// unexpected, invalid-normal-form, or explicitly unsupported typed JSON.
pub fn value_from_diagnostic_json(input: &[u8]) -> Result<Value, Failure> {
    let json: JsonValue =
        serde_json::from_slice(input).map_err(|_| diagnostic_failure("INVALID_JSON"))?;
    parse_diagnostic_value(&json)
}

fn diagnostic_key(key: &Key) -> JsonValue {
    let mut object = JsonMap::new();
    match key {
        Key::Integer(value) => {
            object.insert("type".to_owned(), JsonValue::String("integer".to_owned()));
            object.insert("value".to_owned(), JsonValue::String(value.to_string()));
        }
        Key::Text(value) => {
            object.insert("type".to_owned(), JsonValue::String("text".to_owned()));
            object.insert("value".to_owned(), JsonValue::String(value.clone()));
        }
    }
    JsonValue::Object(object)
}

/// Convert an accepted value to the non-normative typed JSON projection.
#[must_use]
pub fn value_to_diagnostic_json(value: &Value) -> JsonValue {
    let mut object = JsonMap::new();
    match value {
        Value::Integer(value) => {
            object.insert("type".to_owned(), JsonValue::String("integer".to_owned()));
            object.insert("value".to_owned(), JsonValue::String(value.to_string()));
        }
        Value::Bytes(value) => {
            object.insert("hex".to_owned(), JsonValue::String(hex_encode(value)));
            object.insert("type".to_owned(), JsonValue::String("bytes".to_owned()));
        }
        Value::Text(value) => {
            object.insert("type".to_owned(), JsonValue::String("text".to_owned()));
            object.insert("value".to_owned(), JsonValue::String(value.clone()));
        }
        Value::Array(items) => {
            object.insert(
                "items".to_owned(),
                JsonValue::Array(items.iter().map(value_to_diagnostic_json).collect()),
            );
            object.insert("type".to_owned(), JsonValue::String("array".to_owned()));
        }
        Value::Map(entries) => {
            object.insert(
                "entries".to_owned(),
                JsonValue::Array(
                    entries
                        .iter()
                        .map(|entry| {
                            let mut result = JsonMap::new();
                            result.insert("key".to_owned(), diagnostic_key(&entry.key));
                            result
                                .insert("value".to_owned(), value_to_diagnostic_json(&entry.value));
                            JsonValue::Object(result)
                        })
                        .collect(),
                ),
            );
            object.insert("type".to_owned(), JsonValue::String("map".to_owned()));
        }
        Value::Boolean(value) => {
            object.insert("type".to_owned(), JsonValue::String("boolean".to_owned()));
            object.insert("value".to_owned(), JsonValue::Bool(*value));
        }
        Value::Null => {
            object.insert("type".to_owned(), JsonValue::String("null".to_owned()));
        }
    }
    JsonValue::Object(object)
}

/// Stable lowercase hexadecimal encoding.
#[must_use]
pub fn hex_encode(bytes: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut output = String::with_capacity(bytes.len().saturating_mul(2));
    for byte in bytes {
        output.push(char::from(HEX[usize::from(byte >> 4)]));
        output.push(char::from(HEX[usize::from(byte & 0x0f)]));
    }
    output
}

fn hex_nibble(byte: u8) -> Option<u8> {
    match byte {
        b'0'..=b'9' => Some(byte - b'0'),
        b'a'..=b'f' => Some(byte - b'a' + 10),
        b'A'..=b'F' => Some(byte - b'A' + 10),
        _ => None,
    }
}

/// Decode exact hexadecimal diagnostic input.
///
/// # Errors
///
/// Returns stable `expected.top_level` for odd-length or non-hex text.
pub fn hex_decode(input: &str) -> Result<Vec<u8>, Failure> {
    let bytes = input.as_bytes();
    if !bytes.len().is_multiple_of(2) {
        return Err(diagnostic_failure("HEX_ODD_LENGTH"));
    }
    let mut output = Vec::with_capacity(bytes.len() / 2);
    for pair in bytes.chunks_exact(2) {
        let high = hex_nibble(pair[0]).ok_or_else(|| diagnostic_failure("HEX_INVALID"))?;
        let low = hex_nibble(pair[1]).ok_or_else(|| diagnostic_failure("HEX_INVALID"))?;
        output.push((high << 4) | low);
    }
    Ok(output)
}

/// Render one compact JSON value under the diagnostic output cap.
///
/// # Errors
///
/// Returns `resource.diagnostic_bytes` when the encoded line is too large.
pub fn diagnostic_json_with_limit(value: &JsonValue, limits: &Limits) -> Result<String, Failure> {
    limits.check()?;
    let encoded = serde_json::to_string(value)
        .map_err(|_| diagnostic_failure("JSON_SERIALIZATION_FAILED"))?;
    if encoded.len() > limits.max_diagnostic_output_bytes {
        Err(Failure::new(
            ResultClass::ResourceLimit,
            "resource.diagnostic_bytes",
            0,
        ))
    } else {
        Ok(encoded)
    }
}

/// Render one-line, stable-field-order success JSON for the CLI.
///
/// # Errors
///
/// Returns a stable limit failure if the projection exceeds the diagnostic cap.
pub fn success_diagnostic_json(
    canonical: &[u8],
    value: &Value,
    limits: &Limits,
) -> Result<String, Failure> {
    let mut object = JsonMap::new();
    object.insert("code".to_owned(), JsonValue::String("accepted".to_owned()));
    object.insert(
        "cbor_hex".to_owned(),
        JsonValue::String(hex_encode(canonical)),
    );
    object.insert(
        "profile_id".to_owned(),
        JsonValue::String(PROFILE_ID.to_owned()),
    );
    object.insert(
        "result_class".to_owned(),
        JsonValue::String("accepted".to_owned()),
    );
    object.insert("value".to_owned(), value_to_diagnostic_json(value));
    diagnostic_json_with_limit(&JsonValue::Object(object), limits)
}

/// Render one-line, stable-field-order failure JSON for the CLI.
///
/// # Errors
///
/// Returns a stable limit failure if the projection exceeds the diagnostic cap.
pub fn failure_diagnostic_json(failure: &Failure, limits: &Limits) -> Result<String, Failure> {
    let mut object = JsonMap::new();
    object.insert(
        "code".to_owned(),
        JsonValue::String(failure.code.to_owned()),
    );
    object.insert(
        "offset".to_owned(),
        JsonValue::Number(serde_json::Number::from(failure.offset)),
    );
    object.insert(
        "result_class".to_owned(),
        JsonValue::String(failure.class.as_str().to_owned()),
    );
    diagnostic_json_with_limit(&JsonValue::Object(object), limits)
}
