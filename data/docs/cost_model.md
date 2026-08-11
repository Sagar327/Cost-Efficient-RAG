# Cost model

The purpose of this project is not to claim a universal vector database price. It uses an explicit assumption-based comparison so that the assumptions can be changed.

For the local Chroma option, the model assumes a small always-on VM costing $5/month and disk costing $0.10/GB-month.

For a managed vector database, the illustrative model assumes $0.25/GB-month storage and $0.05 per million query operations. These are placeholders for scenario analysis, not vendor quotes.

The embedding model is 384-dimensional float32. A raw vector is therefore 384 * 4 = 1536 bytes. The model adds a 1.5x allowance for index and metadata overhead.

At 100K vectors, 1M vectors, and 10M vectors, the script reports estimated storage and monthly costs for both approaches.

The local store is attractive for lightly queried indexes because there is no dedicated managed vector service to keep running. A managed service becomes more attractive as availability, concurrency, scaling, operational burden, and managed features become more important than minimizing fixed infrastructure cost.
