import time

from forest.trees import ExperienceTree, ForestStore


def forest_forget(domain: str, threshold: float = 0.1) -> int:
    store = ForestStore(domain)
    trees = store.all()
    before = len(trees)
    trees = [t for t in trees if t.weight >= threshold]
    removed = before - len(trees)
    store.replace_all(trees)
    return removed


def apply_decay(trees: list[ExperienceTree], days: float = 1.0) -> list[ExperienceTree]:
    now = time.time()
    for t in trees:
        age_days = (now - t.timestamp) / 86400.0
        t.weight *= 0.95 ** (age_days / days)
    return trees


def forest_consolidate(domain: str, similarity_threshold: float = 0.7) -> int:
    store = ForestStore(domain)
    trees = store.all()
    if not trees:
        return 0

    merged = 0
    kept = []
    used = set()
    for i, a in enumerate(trees):
        if i in used:
            continue
        cluster = [a]
        for j, b in enumerate(trees):
            if j <= i or j in used:
                continue
            sim = _tree_similarity(a, b)
            if sim >= similarity_threshold:
                cluster.append(b)
                used.add(j)
        if len(cluster) > 1:
            merged += len(cluster) - 1
            avg_weight = sum(t.weight for t in cluster) / len(cluster)
            avg_outcome = sum(t.outcome for t in cluster) / len(cluster)
            a.weight = avg_weight
            a.outcome = avg_outcome
            a.tags = list(set(t for t_ in cluster for t in t_.tags))
        kept.append(a)

    store.replace_all(kept)
    return merged


def _tree_similarity(a: ExperienceTree, b: ExperienceTree) -> float:
    if a.domain != b.domain:
        return 0.0
    words_a = set(a.approach.lower().split())
    words_b = set(b.approach.lower().split())
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / len(words_a | words_b)
