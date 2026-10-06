"""Streaming candidate output writer for HashForge."""

import os
from typing import Iterator, Dict, Any, Optional, Callable
from ..hashcat.discovery import format_size


def stream_candidates_to_file(
    candidate_stream: Iterator[str],
    output_path: str = os.path.join("output", "hashforge_wordlist.txt"),
    on_progress: Optional[Callable[[int], None]] = None,
    progress_interval: int = 25000,
) -> Dict[str, Any]:
    """Stream candidate strings line-by-line into a UTF-8 encoded .txt file.

    Guarantees:
    - Never buffers entire candidate list in memory: writes directly to file stream.
    - Automatic directory creation.
    - Strictly UTF-8 encoded.
    - Returns execution statistics.
    """
    # Ensure target directory exists
    target_dir = os.path.dirname(output_path)
    if target_dir and not os.path.isdir(target_dir):
        os.makedirs(target_dir, exist_ok=True)

    count = 0
    with open(output_path, "w", encoding="utf-8", newline="\n") as out_f:
        for candidate in candidate_stream:
            out_f.write(candidate + "\n")
            count += 1
            if on_progress and (count % progress_interval == 0):
                on_progress(count)

    # Determine file size
    size_bytes = os.path.getsize(output_path) if os.path.isfile(output_path) else 0

    return {
        "count": count,
        "output_path": output_path,
        "size_bytes": size_bytes,
        "size_formatted": format_size(size_bytes),
    }
