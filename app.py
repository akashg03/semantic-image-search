"""
Semantic image search MVP: embed local images with Gemini multimodal embeddings, search with text via FAISS.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import faiss
import google.generativeai as genai
import numpy as np
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

# Gemini Embedding 2 (multimodal). The `google-generativeai` API uses this model id
# for text + image in one space. (Some docs use other names; this is the public Gemini API id.)
DEFAULT_EMBEDDING_MODEL = "gemini-embedding-2-preview"

EMBEDDING_MODEL = os.environ.get("GEMINI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)

DEFAULT_TOP_K = 2


def _default_top_k() -> int:
    """Number of search hits from env ``TOP_K`` (falls back to ``DEFAULT_TOP_K``)."""
    raw = os.environ.get("TOP_K", str(DEFAULT_TOP_K)).strip()
    try:
        k = int(raw)
    except ValueError as exc:
        raise RuntimeError(f"TOP_K must be an integer, got {raw!r}") from exc
    if k < 1:
        raise RuntimeError(f"TOP_K must be >= 1, got {k}")
    return k


DEFAULT_IMAGE_DIR = "images"


def _default_image_dir() -> str:
    """Root folder to scan for images: ``IMAGE_DIR`` in env, else ``DEFAULT_IMAGE_DIR``."""
    raw = os.environ.get("IMAGE_DIR", DEFAULT_IMAGE_DIR).strip()
    return raw if raw else DEFAULT_IMAGE_DIR


DATA_DIR = Path(__file__).resolve().parent / "data"
FAISS_PATH = DATA_DIR / "image_index.faiss"
PATHS_PATH = DATA_DIR / "image_paths.json"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}


def _configure_genai() -> None:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to a .env file in this directory "
            "(see instructions in the project README or your notes)."
        )
    genai.configure(api_key=key)


def _embed_image(path: Path) -> list[float]:
    try:
        img = Image.open(path)
        img.load()
    except OSError as exc:
        raise ValueError(f"Cannot open or decode image: {path}") from exc

    try:
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        result = genai.embed_content(model=EMBEDDING_MODEL, content=img)
    finally:
        img.close()

    return result["embedding"]


def _embed_text(text: str) -> list[float]:
    result = genai.embed_content(model=EMBEDDING_MODEL, content=text)
    return result["embedding"]


def index_images(image_dir: str | Path) -> None:
    """
    Embed all images under ``image_dir`` and persist a FAISS index + path list under ``data/``.
    """
    _configure_genai()
    root = Path(image_dir).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Not a directory: {root}")

    paths: list[Path] = []
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS:
            paths.append(p)

    if not paths:
        raise ValueError(f"No images found under {root} (supported: {sorted(IMAGE_EXTENSIONS)})")

    vectors: list[np.ndarray] = []
    kept_paths: list[str] = []

    for path in paths:
        try:
            emb = _embed_image(path)
            v = np.asarray(emb, dtype=np.float32).reshape(1, -1)
            faiss.normalize_L2(v)
            vectors.append(v)
            kept_paths.append(str(path))
        except (ValueError, OSError, RuntimeError) as exc:
            print(f"[skip] {path}: {exc}", file=sys.stderr)

    if not vectors:
        raise RuntimeError("No embeddings were produced; all image files failed.")

    mat = np.vstack(vectors)
    dim = mat.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(mat)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(FAISS_PATH))
    PATHS_PATH.write_text(json.dumps(kept_paths, indent=2), encoding="utf-8")
    print(f"Indexed {len(kept_paths)} images → {FAISS_PATH}")


def search(query: str, top_k: int | None = None) -> list[str]:
    """
    Embed ``query`` and return the top ``top_k`` image paths by cosine similarity (via normalized IP).
    If ``top_k`` is None, uses ``TOP_K`` from the environment (see ``_default_top_k``).
    """
    if top_k is None:
        top_k = _default_top_k()
    _configure_genai()
    if not FAISS_PATH.is_file() or not PATHS_PATH.is_file():
        raise FileNotFoundError(
            f"Index missing. Run `index` first. Expected {FAISS_PATH} and {PATHS_PATH}."
        )

    paths: list[str] = json.loads(PATHS_PATH.read_text(encoding="utf-8"))
    index = faiss.read_index(str(FAISS_PATH))

    q = np.asarray(_embed_text(query), dtype=np.float32).reshape(1, -1)
    faiss.normalize_L2(q)

    k = min(top_k, len(paths))
    if k < 1:
        return []

    _scores, indices = index.search(q, k)
    out: list[str] = []
    for idx in indices[0]:
        if idx < 0 or idx >= len(paths):
            continue
        out.append(paths[idx])
    return out


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Semantic image search (Gemini embeddings + FAISS)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_index = sub.add_parser("index", help="Build FAISS index from a folder of images")
    p_index.add_argument(
        "--dir",
        "-d",
        default=None,
        metavar="DIR",
        help="Directory containing images (recursive). Overrides IMAGE_DIR in .env; if omitted, uses IMAGE_DIR or ./images",
    )

    p_search = sub.add_parser("search", help="Search indexed images by text")
    p_search.add_argument("query", help="Natural language query")
    p_search.add_argument(
        "-k",
        "--top-k",
        type=int,
        default=None,
        metavar="N",
        help="Number of results (overrides TOP_K in .env; default from TOP_K, else 2)",
    )

    args = parser.parse_args()

    try:
        if args.command == "index":
            image_root = args.dir if args.dir is not None else _default_image_dir()
            index_images(image_root)
        else:
            for path in search(args.query, top_k=args.k):
                print(path)
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    _cli()
