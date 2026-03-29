# Concepts

**Model note:** The Gemini API exposes multimodal **Gemini Embedding 2** as `gemini-embedding-2-preview`. Older or alternate docs may use other names; this project uses that id with `google.generativeai`’s `embed_content`.

---

## Multimodal Vector Spaces

A **multimodal vector space** is a shared embedding space where inputs of different types (for example, text and images) are mapped to vectors of fixed dimension so that semantically related items lie close together. That allows querying with text and retrieving images (or other modalities) that are “about” the same concepts, without relying on keywords or tags.

## Cosine Similarity

**Cosine similarity** measures the cosine of the angle between two vectors. For embeddings it is a common choice because it focuses on direction (semantic orientation) rather than magnitude. For unit-normalized vectors, inner product search (as used with FAISS `IndexFlatIP` on normalized vectors) is equivalent to cosine similarity.

## Latent Representation

A **latent representation** is a compact vector produced by a model that encodes high-level patterns in the data rather than raw pixels or characters. Embeddings are latent representations: they distill images or text into coordinates that capture meaning for similarity and retrieval.
