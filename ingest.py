"""Ingest documents into Supabase pgvector.

Usage:
    python ingest.py path/to/file.pdf path/to/notes.md path/to/dir/
"""
import sys
from pathlib import Path

from pypdf import PdfReader

from backend.chunking import chunk_text
from backend.embeddings import embed_documents
from backend.db import insert_chunks

SUPPORTED_EXTS = {".txt", ".md", ".pdf"}
EMBED_BATCH = 64


def read_file(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8", errors="replace")


def collect_files(args: list[str]) -> list[Path]:
    files: list[Path] = []
    for arg in args:
        p = Path(arg).expanduser().resolve()
        if not p.exists():
            print(f"skip (not found): {p}")
            continue
        if p.is_dir():
            for child in p.rglob("*"):
                if child.is_file() and child.suffix.lower() in SUPPORTED_EXTS:
                    files.append(child)
        elif p.suffix.lower() in SUPPORTED_EXTS:
            files.append(p)
        else:
            print(f"skip (unsupported ext): {p}")
    return files


def ingest_file(path: Path) -> int:
    print(f"reading {path}")
    text = read_file(path)
    chunks = chunk_text(text)
    if not chunks:
        print(f"  no content extracted, skipping")
        return 0

    print(f"  {len(chunks)} chunks; embedding...")
    rows: list[dict] = []
    for i in range(0, len(chunks), EMBED_BATCH):
        batch = chunks[i : i + EMBED_BATCH]
        vectors = embed_documents(batch)
        for j, (chunk, vec) in enumerate(zip(batch, vectors)):
            rows.append(
                {
                    "source": path.name,
                    "chunk_index": i + j,
                    "content": chunk,
                    "embedding": vec,
                }
            )

    print(f"  inserting {len(rows)} rows")
    insert_chunks(rows)
    return len(rows)


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python ingest.py <file_or_dir> [<file_or_dir> ...]")
        sys.exit(1)

    files = collect_files(sys.argv[1:])
    if not files:
        print("no supported files found")
        sys.exit(1)

    total = 0
    for f in files:
        total += ingest_file(f)
    print(f"\ndone — {total} chunks inserted across {len(files)} files")


if __name__ == "__main__":
    main()
