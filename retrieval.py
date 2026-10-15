import math
import re


STOP_WORDS = {
    "a", "an", "and", "are", "at", "be", "can", "do", "does", "for",
    "from", "how", "i", "in", "is", "it", "me", "of", "on", "or", "the",
    "to", "was", "we", "what", "when", "where", "which", "who", "why",
    "with", "you", "your", "held", "tell", "please",
}


def tokenize(text):
    return [
        token
        for token in re.findall(r"[\w]+", text.casefold(), flags=re.UNICODE)
        if token not in STOP_WORDS and len(token) > 1
    ]


def load_documents(data):
    """Return validated knowledge passages from the small JSON knowledge base."""
    docs = data.get("documents", [])
    valid = []
    for item in docs:
        text = str(item.get("text", "")).strip()
        source = str(item.get("source", "")).strip()
        if text and source:
            valid.append(
                {
                    "text": text,
                    "source": source,
                    "page": item.get("page"),
                    "url": str(item.get("url", "")).strip() or None,
                    "language": str(item.get("language", "en")).strip() or "en",
                    "verified_on": str(item.get("verified_on", "")).strip() or None,
                }
            )
    return valid


def _term_counts(tokens):
    counts = {}
    for token in tokens:
        counts[token] = counts.get(token, 0) + 1
    return counts


def search_documents(query, documents, limit=3, language=None):
    """Small local TF-IDF search; each result keeps its source metadata."""
    query_counts = _term_counts(tokenize(query))
    if not query_counts or not documents:
        return []

    eligible = [
        item for item in documents
        if language in (None, "auto") or item.get("language", "en") == language
    ]
    if not eligible:
        eligible = documents
    doc_tokens = [tokenize(item["text"]) for item in eligible]
    document_frequency = {}
    for tokens in doc_tokens:
        for term in set(tokens):
            document_frequency[term] = document_frequency.get(term, 0) + 1

    total_docs = len(eligible)

    def weighted(counts):
        vector = {}
        for term, count in counts.items():
            idf = math.log((1 + total_docs) / (1 + document_frequency.get(term, 0))) + 1
            vector[term] = (1 + math.log(count)) * idf
        return vector

    query_vector = weighted(query_counts)
    query_norm = math.sqrt(sum(value * value for value in query_vector.values())) or 1.0
    ranked = []
    for item, tokens in zip(eligible, doc_tokens):
        vector = weighted(_term_counts(tokens))
        norm = math.sqrt(sum(value * value for value in vector.values())) or 1.0
        score = sum(value * vector.get(term, 0.0) for term, value in query_vector.items())
        score /= query_norm * norm
        if score > 0:
            ranked.append({**item, "score": score})
    ranked.sort(key=lambda result: result["score"], reverse=True)
    return ranked[:limit]


def source_label(result):
    if result.get("page") is not None:
        return f'{result["source"]}, page {result["page"]}'
    return result["source"]

