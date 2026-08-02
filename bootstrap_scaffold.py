#!/usr/bin/env python3
"""One-shot, integrity-checked materializer for the StatQED repository scaffold."""

from __future__ import annotations

import base64
import hashlib
import json
import shutil
import zlib
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
PAYLOAD_DIR = ROOT / "bootstrap_payload"
EXPECTED_FILE_COUNT = 226
EXPECTED_PAYLOAD_SHA256 = "718d7bc932d97d83dc50747b2bb0958d84780695fda0b8eed8bac6e26d897631"
EXPECTED_DECODED_SHA256 = "9768d6233e0348231e1db8fc9f0cb935c7e0a16392982b7b7c5c23390d49296f"

# This edit intentionally retriggers the one-shot materialization workflow.
# Each staged chunk is validated independently. A GitHub connector edge case dropped
# the first Base64 character from some chunks, so the sole permitted repair is to
# restore that known character and then require the original SHA-256 digest.
CHUNK_SPECS = (
    ("part-000.txt", 20_000, "e", "a051c4644e161dba587cec81deb20d7e322c698d48d4f6c17eab5d52b65fa63e"),
    ("part-001.txt", 20_000, "c", "94bc2bcfa37aeb0c628094430a481c815bd4f314bc961844fd103e4ce72dab8e"),
    ("part-002.txt", 40_000, "z", "4bb1e6ee230d2acf0cc583665298bac18b55537b7b47b24d23af8048ef236e43"),
    ("part-003.txt", 40_000, "l", "80d4b2fdd802e6855a8add1a9019974bc0935d60c8702c743d7f472b573da97d"),
    ("part-004.txt", 22_044, "8", "41f540f251217d17af3555d2ca52f1847ebcc3df3d3705931436ad4ae1b03f1c"),
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def restore_and_validate_chunk(
    path: Path,
    expected_length: int,
    expected_first: str,
    expected_sha256: str,
) -> str:
    raw = path.read_text(encoding="ascii").strip()
    candidates = [raw]
    if not raw.startswith(expected_first):
        candidates.append(expected_first + raw)

    for candidate in candidates:
        if len(candidate) == expected_length and sha256_text(candidate) == expected_sha256:
            return candidate

    raise RuntimeError(
        "Payload chunk failed integrity validation: "
        f"{path.name}; observed_length={len(raw)}; "
        f"observed_sha256={sha256_text(raw)}; "
        f"prefix={raw[:12]!r}; suffix={raw[-12:]!r}"
    )


def safe_target(relative_name: str) -> Path:
    pure = PurePosixPath(relative_name)
    if pure.is_absolute() or not pure.parts or ".." in pure.parts:
        raise ValueError(f"Unsafe scaffold path: {relative_name!r}")
    target = (ROOT / Path(*pure.parts)).resolve()
    target.relative_to(ROOT.resolve())
    return target


def main() -> None:
    chunks: list[str] = []
    for filename, length, first, digest in CHUNK_SPECS:
        path = PAYLOAD_DIR / filename
        if not path.is_file():
            raise RuntimeError(f"Missing payload chunk: {path}")
        chunks.append(restore_and_validate_chunk(path, length, first, digest))

    payload = "".join(chunks)
    if sha256_text(payload) != EXPECTED_PAYLOAD_SHA256:
        raise RuntimeError("Combined payload failed SHA-256 validation")

    compressed = base64.b64decode(payload, validate=True)
    decoded = zlib.decompress(compressed)
    if hashlib.sha256(decoded).hexdigest() != EXPECTED_DECODED_SHA256:
        raise RuntimeError("Decoded scaffold failed SHA-256 validation")

    files: dict[str, str] = json.loads(decoded.decode("utf-8"))
    if len(files) != EXPECTED_FILE_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_FILE_COUNT} scaffold files, found {len(files)}"
        )

    for relative_name, content in files.items():
        if not isinstance(relative_name, str) or not isinstance(content, str):
            raise TypeError("Scaffold mapping must contain only string paths and contents")
        target = safe_target(relative_name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")

    # Remove the transport mechanism. The permanent repository should contain only
    # the reviewed scaffold and its normal guardrails.
    for temporary in (
        ROOT / "bootstrap_scaffold.py",
        ROOT / ".github" / "workflows" / "materialize-scaffold.yml",
    ):
        if temporary.exists():
            temporary.unlink()
    shutil.rmtree(PAYLOAD_DIR)

    print(f"Materialized {len(files)} integrity-checked StatQED scaffold files.")


if __name__ == "__main__":
    main()
