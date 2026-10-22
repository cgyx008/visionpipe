import hashlib
import json
import os
import time
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any


def calc_hash(
    p: str | Path,
    chunk_size: int = 4 * 1024 * 1024,
    method: str = "md5",
) -> str | None:
    """
    Calculate the hash of a file.

    Args:
        p: file path
        chunk_size: chunk size of each file block read, default 4 MB
        method: md5 or sha26

    Returns:
        (str | None): the hash of a file or None if raise error
    """
    retry = 3
    for i in range(retry):
        try:
            m_hash = hashlib.sha256() if method == "sha256" else hashlib.md5()
            with open(p, "rb") as f:  # binary mode
                while chunk := f.read(chunk_size):
                    m_hash.update(chunk)
            return m_hash.hexdigest()
        except OSError as e:
            if i < retry - 1:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                print(f"{ts} - {p} raises: {e}. Retrying {i + 2} / {retry}")
                time.sleep(1)

    return None


def append_jsonl(p: str | Path, d: Mapping[str, Any]) -> None:
    append_line = json.dumps(d, ensure_ascii=False) + "\n"
    exists = False
    if Path(p).exists():
        with open(p, encoding="utf-8") as f:
            for line in f:
                if line == append_line:
                    exists = True
                    break
    if not exists:
        os.umask(0)
        Path(p).parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(append_line)
