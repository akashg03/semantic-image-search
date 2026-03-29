# Local FAISS vs Cloud Vector Databases

## Privacy

**Local FAISS** keeps vectors and metadata on disk (or in memory) on a machine you control. Image paths and embedding files never leave your environment unless you choose to copy them. **Cloud vector databases** store indexed vectors (and often metadata) on a provider’s infrastructure. Even with encryption and access controls, you must trust the vendor’s security model, regions, and compliance story. For sensitive or proprietary images, local indexing minimizes third-party exposure; cloud solutions trade some control for convenience and scale.

## Cost

**FAISS** is free to run: you pay for your own compute and storage, and for API calls to the embedding model (here, Gemini) when you build or refresh the index. There is no per-query vector DB fee. **Managed cloud vector DBs** typically charge for hosted capacity, replication, backup, and sometimes per-operation pricing on top of embedding generation. For a small, static set of images (this MVP’s 10–20), local FAISS is usually cheaper and simpler. At large scale (millions of vectors, high QPS, multi-region), a cloud DB’s operational cost can be justified by reduced engineering effort and built-in scaling.

## Summary

Use **local FAISS** when you want maximum privacy control and minimal recurring infrastructure cost for modest data sizes. Consider a **cloud vector DB** when you need managed scaling, high availability, or team-wide shared indexes and the privacy/cost trade-off is acceptable.
