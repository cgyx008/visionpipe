import hashlib
import json
from pathlib import Path

from visionpipe.file import append_jsonl, calc_hash


def test_append_jsonl_creates_parent_dirs(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "metadata.jsonl"

    append_jsonl(target, {"path": "video.mp4", "width": 1920})

    assert target.is_file()
    assert json.loads(target.read_text(encoding="utf-8")) == {
        "path": "video.mp4",
        "width": 1920,
    }


def test_append_jsonl_skips_exact_duplicates(tmp_path: Path) -> None:
    target = tmp_path / "metadata.jsonl"
    record = {"path": "video.mp4", "width": 1920}

    append_jsonl(target, record)
    append_jsonl(target, record)

    assert len(target.read_text(encoding="utf-8").splitlines()) == 1


def test_append_jsonl_appends_different_records(tmp_path: Path) -> None:
    target = tmp_path / "metadata.jsonl"

    append_jsonl(target, {"path": "a.mp4"})
    append_jsonl(target, {"path": "b.mp4"})

    lines = target.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert [json.loads(line)["path"] for line in lines] == ["a.mp4", "b.mp4"]


def test_calc_hash_matches_hashlib(tmp_path: Path) -> None:
    target = tmp_path / "data.bin"
    target.write_bytes(b"visionpipe")

    expected = hashlib.md5(b"visionpipe").hexdigest()
    assert calc_hash(target) == expected
