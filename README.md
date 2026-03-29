# Semantic Image Search (MVP)

Local **text → image** search over a folder of pictures: images are embedded with **Google Gemini** multimodal embeddings (**Gemini Embedding 2**), stored in a **FAISS** index on disk, and queries are plain English (or any text the model understands).

This repo is safe to **push to GitHub** and **share with others**. Secrets stay in `.env` (ignored by git). Others clone the repo, add their **own** API key, and run the same commands.

---

## What you need

- **Python 3.10+** (3.12 recommended)
- A **Gemini API key** ([Google AI Studio](https://aistudio.google.com/apikey)) — free tier is enough to try this

---

## Quick start

### 1. Clone or copy the project

```bash
cd semantic-image-search
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

Copy the example env file and add your key:

```bash
cp .env.example .env
```

Edit **`.env`**:

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | **Yes** | Your key from AI Studio |
| `IMAGE_DIR` | No | Default folder to **index** (images only; **all subfolders** are scanned). Used when you run `python app.py index` **without** `--dir` (default `images`, i.e. `./images` relative to the project) |
| `TOP_K` | No | Default number of file paths printed for `search` when you omit `-k` (default `2`) |
| `GEMINI_EMBEDDING_MODEL` | No | Override embedding model (default `gemini-embedding-2-preview`) |

Never commit `.env`. **`.env.example`** is a template without secrets and **is** meant to be committed.

### 3. Add images

Put **10–20** (or more) images under a single root folder (for example `./images`). You can use **nested subfolders** (e.g. `images/singapore/`, `images/japan/`); indexing walks the tree recursively. Supported extensions: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.bmp`.

Set **`IMAGE_DIR`** in `.env` if you want a default root (absolute or relative path). Example:

```env
IMAGE_DIR=/Users/you/Pictures/vacation
```

### 4. Build the index

**Precedence:** `python app.py index --dir /some/path` **overrides** `IMAGE_DIR` in `.env`. If you omit `--dir`, the app uses **`IMAGE_DIR`**, or `./images` if `IMAGE_DIR` is unset.

```bash
# Uses IMAGE_DIR from .env, or ./images
python app.py index

# Explicit path (ignores IMAGE_DIR for this run)
python app.py index --dir ./images
```

This writes under `data/`:

- `image_index.faiss` — vector index  
- `image_paths.json` — paths in the same order as vectors  

These files are **gitignored** (they are large, machine-specific, and may contain paths you don’t want in the repo).

### 5. Search

```bash
python app.py search "sunset over water"
```

Uses **`TOP_K`** from `.env` for how many paths to print. Override per run:

```bash
python app.py search "basketball" -k 5
```

`-k` / `--top-k` always wins over `TOP_K` in `.env`.

---

## Sharing with someone else

1. **Push** this repository to GitHub (or send a zip). Include **`.env.example`**; do **not** include `.env` or `data/*.faiss` / `data/image_paths.json` (already ignored).
2. They **clone**, create a **venv**, `pip install -r requirements.txt`, copy `.env.example` → `.env`, and paste **their own** `GEMINI_API_KEY`.
3. They add **their** images and run `index` then `search`.

**Billing / limits:** Embedding calls use the Gemini API under their key and Google’s quotas. **You do not host their API** — they call Google from their machine.

**Optional:** If you use multiple GitHub accounts, use an SSH host alias so personal repos use the right key (see notes in your own `PERSONAL_GITHUB_SSH.md` if you use that pattern).

---

## CLI reference

```text
python app.py index  [-d DIR]     # DIR defaults to IMAGE_DIR in .env, else ./images
python app.py search QUERY [-k N]  # N overrides TOP_K in .env
```

---

## Project files

| File | Purpose |
|------|---------|
| `app.py` | `index_images()`, `search()`, CLI |
| `requirements.txt` | Python dependencies |
| `.env.example` | Safe template for `.env` (committed) |
| `skills.md` | Short notes on vectors / cosine similarity / latent space |
| `design.md` | FAISS vs cloud vector DB (privacy & cost) |

---

## Troubleshooting

- **`GEMINI_API_KEY is not set`** — Create `.env` next to `app.py` with `GEMINI_API_KEY=...`.
- **`Index missing`** — Run `python app.py index` (with `IMAGE_DIR` set or images under `./images`) or `python app.py index --dir /path/to/images` first.
- **`TOP_K must be...`** — Set `TOP_K` to a positive integer in `.env`.
- **Deprecation warning** from `google-generativeai` — Expected; Google recommends migrating to `google.genai` later; this MVP still uses `google-generativeai` as specified.

---

## License

Add a `LICENSE` file if you want a clear open-source terms for collaborators. This README does not impose a license by itself.
