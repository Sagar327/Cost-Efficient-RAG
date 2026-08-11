import time
import requests


SYSTEM_PROMPT = """You are a grounded question-answering assistant.

Use ONLY the supplied context to answer the user's question.

IMPORTANT RULES:
1. Answer ONLY the specific question that was asked.
2. Every factual claim must be directly supported by the supplied context.
3. Do NOT combine unrelated facts from different parts of the context.
4. A retrieved chunk may contain information that is irrelevant to the question. IGNORE it.
5. Pay close attention to the exact event, person, object, and time mentioned in the question.
6. Do not add information merely because it appears somewhere in the retrieved context.
7. Cite the context chunk that directly supports each factual claim using [1], [2], etc.
8. Only cite a chunk if it actually supports the claim.
9. Do not invent citations, facts, events, or source names.
10. If the context does not contain enough evidence to answer the question, say exactly:
"I don't have enough relevant context to answer that."

Keep the answer concise and directly answer the question."""


def generate_answer(
    question: str,
    contexts: list[dict],
    base_url: str,
    api_key: str,
    model: str,
):
    if not api_key and "localhost" not in base_url and "127.0.0.1" not in base_url:
        raise RuntimeError(
            "LLM_API_KEY is not configured. Set it in .env, "
            "or point LLM_BASE_URL to a local OpenAI-compatible server."
        )

    context_text = "\n\n".join(
        f"[{i}] SOURCE={c['source']} CHUNK={c['chunk_index']}\n{c['text']}"
        for i, c in enumerate(contexts, 1)
    )

    user = f"""Question:
{question}

Retrieved context:
{context_text}

Answer the question using only the retrieved context.
Focus on the exact question and ignore unrelated information.
"""

    headers = {
        "Content-Type": "application/json"
    }

    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user
            },
        ],
    }

    t0 = time.perf_counter()

    r = requests.post(
        f"{base_url}/chat/completions",
        json=payload,
        headers=headers,
        timeout=120,
    )

    latency = (time.perf_counter() - t0) * 1000

    r.raise_for_status()

    data = r.json()

    choice = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})

    return choice, latency, usage