# Retrieval and answer evaluation

The evaluation set contains 15 fixed questions. Each question has gold source information and keywords that define what counts as a relevant chunk.

Retrieval quality is measured using Recall@k, Hit Rate, Mean Reciprocal Rank (MRR), nDCG, and context precision. Recall@k and Hit Rate are binary for this compact benchmark: a query succeeds when at least one relevant gold chunk is retrieved. MRR rewards putting the first relevant chunk near the top. nDCG accounts for rank. Context precision is the fraction of retrieved chunks judged relevant by the gold criteria.

The retrieval depth k is configurable. Increasing k can improve recall but increases prompt context, LLM input tokens, and latency. The evaluation script accepts k so the trade-off can be measured instead of assumed.

Latency is logged separately for retrieval and LLM generation. p50 is the median query latency and p95 is the 95th percentile. Token usage is recorded from an OpenAI-compatible response when the provider returns usage fields.

For answer evaluation, the system can be judged on faithfulness and answer relevance. A faithful answer is supported by the retrieved chunks; an irrelevant answer does not address the question. The safest behavior for missing evidence is an explicit refusal rather than a guessed answer.
