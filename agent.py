import json
import os
import urllib.error
import urllib.request

from retrieval import search_documents, source_label


OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
GEMMA_MODEL = os.environ.get("GEMMA_MODEL", "gemma4:e2b")
MIN_EVIDENCE_SCORE = 0.12

FALLBACK = (
    "I couldn’t confirm that from the information available to me. "
    "Please check with the relevant university office."
)


def _generate_with_gemma(question, evidence):
    context = "\n\n".join(
        f"Source: {source_label(item)}\nInformation: {item['text']}"
        for item in evidence
    )
    payload = {
        "model": GEMMA_MODEL,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are IUL Saarthi, a campus information assistant prototype. "
                    "Answer only using the supplied information. Do not add facts, "
                    "dates, policies, or contact details that are not in it. "
                    "If the information does not answer the question, say you cannot "
                    "confirm it and advise the student to contact the relevant office. "
                    "Keep the answer concise."
                ),
            },
            {
                "role": "user",
                "content": f"Question: {question}\n\nAvailable information:\n{context}",
            },
        ],
        "options": {"temperature": 0.1},
    }
    request = urllib.request.Request(
        f"{OLLAMA_HOST}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        result = json.loads(response.read().decode("utf-8"))
    return result.get("message", {}).get("content", "").strip()


def answer_question(question, documents):
    """Agent controller: retrieve evidence, gate unsupported queries, then use Gemma."""
    matches = search_documents(question, documents)
    sources = list(dict.fromkeys(source_label(item) for item in matches))
    if not matches or matches[0]["score"] < MIN_EVIDENCE_SCORE:
        return {"answer": FALLBACK, "sources": [], "evidence": [], "notice": None}

    evidence = [item for item in matches if item["score"] >= MIN_EVIDENCE_SCORE]
    if not evidence:
        return {"answer": FALLBACK, "sources": [], "evidence": [], "notice": None}

    try:
        answer = _generate_with_gemma(question, evidence)
        if not answer:
            return {
                "answer": FALLBACK,
                "sources": sources,
                "evidence": evidence,
                "notice": None,
            }
        return {
            "answer": answer,
            "sources": sources,
            "evidence": evidence,
            "notice": None,
        }
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        return {
            "answer": (
                "I found related information, but Gemma is not available right now, "
                "so I can’t generate a grounded answer. Please start Ollama and try again."
            ),
            "sources": sources,
            "evidence": evidence,
            "notice": f"Local model connection: {error}",
        }

