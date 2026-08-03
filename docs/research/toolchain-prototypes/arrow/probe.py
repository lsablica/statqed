#!/usr/bin/env python3
"""PyArrow side of the non-normative Arrow interoperability probe."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pyarrow as pa
import pyarrow.ipc as ipc


def fixture() -> pa.Table:
    schema = pa.schema(
        [
            pa.field("id", pa.int64(), nullable=False),
            pa.field("label", pa.string(), nullable=True),
            pa.field("payload", pa.binary(), nullable=True),
        ]
    )
    table = pa.Table.from_arrays(
        [
            pa.array([1, 2, 3], type=pa.int64()),
            pa.array(["alpha", None, "e\N{COMBINING ACUTE ACCENT}"], type=pa.string()),
            pa.array([b"\x00\xff", b"", None], type=pa.binary()),
        ],
        schema=schema,
    )
    table.validate(full=True)
    return table


def file_bytes(table: pa.Table) -> bytes:
    sink = pa.BufferOutputStream()
    with ipc.new_file(sink, table.schema) as writer:
        writer.write_table(table)
    return sink.getvalue().to_pybytes()


def stream_bytes(table: pa.Table) -> bytes:
    sink = pa.BufferOutputStream()
    with ipc.new_stream(sink, table.schema) as writer:
        writer.write_table(table)
    return sink.getvalue().to_pybytes()


def check_table(table: pa.Table) -> None:
    table.validate(full=True)
    assert table.schema == fixture().schema
    assert table.to_pylist() == fixture().to_pylist()


def command_self() -> None:
    table = fixture()
    file_a = file_bytes(table)
    file_b = file_bytes(table)
    stream_a = stream_bytes(table)
    stream_b = stream_bytes(table)
    assert file_a == file_b
    assert stream_a == stream_b
    assert file_a != stream_a
    check_table(ipc.open_file(pa.BufferReader(file_a)).read_all())
    check_table(ipc.open_stream(pa.BufferReader(stream_a)).read_all())
    build = pa.cpp_build_info
    print(f"pyarrow_version={pa.__version__}")
    print(f"arrow_cpp_version={build.version}")
    print(f"compiler={build.compiler_id}-{build.compiler_version}")
    print("ipc_metadata_default=V5")
    print("stream_repeat_equal=true")
    print("file_repeat_equal=true")
    print("stream_file_bytes_equal=false")
    print("round_trip_equal=true")
    print(f"stream_len={len(stream_a)}")
    print(f"file_len={len(file_a)}")
    print(f"physical_file_sha256={hashlib.sha256(file_a).hexdigest()}")


def command_write(path: Path) -> None:
    path.write_bytes(file_bytes(fixture()))
    print("python_wrote_file=true")


def command_read(path: Path) -> None:
    check_table(ipc.open_file(path).read_all())
    print("python_read_foreign_file=true")


def command_reject(path: Path) -> None:
    try:
        ipc.open_file(path).read_all()
    except (pa.ArrowInvalid, OSError) as error:
        print(f"python_rejected_malformed=true error={type(error).__name__}:{error}")
        return
    raise AssertionError("malformed Arrow file unexpectedly accepted")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("self")
    for name in ("write-file", "read-file", "reject-file"):
        child = sub.add_parser(name)
        child.add_argument("path", type=Path)
    args = parser.parse_args()
    if args.command == "self":
        command_self()
    elif args.command == "write-file":
        command_write(args.path)
    elif args.command == "read-file":
        command_read(args.path)
    else:
        command_reject(args.path)


if __name__ == "__main__":
    main()
