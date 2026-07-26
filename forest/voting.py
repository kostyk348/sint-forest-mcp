from collections import defaultdict

from forest.trees import ExperienceTree, ForestStore


def _similarity(a: str, b: str) -> float:
    words_a = set(a.lower().split())
    words_b = set(b.lower().split())
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / len(words_a | words_b)


def forest_vote(
    domain: str, problem: str, candidate_approaches: list[str]
) -> dict[str, float]:
    store = ForestStore(domain)
    trees = store.all()
    if not trees or not candidate_approaches:
        return {}

    scores = defaultdict(float)
    for tree in trees:
        outcome_factor = max(0.0, tree.outcome)
        for candidate in candidate_approaches:
            sim = _similarity(tree.approach, candidate)
            scores[candidate] += sim * tree.weight * outcome_factor

    total = sum(scores.values())
    if total > 0:
        for c in scores:
            scores[c] /= total

    return dict(sorted(scores.items(), key=lambda x: -x[1]))


def forest_vote_borda(domain: str, candidate_approaches: list[str]) -> dict[str, float]:
    store = ForestStore(domain)
    trees = store.all()
    if not trees or not candidate_approaches:
        return {}

    n = len(candidate_approaches)
    scores = defaultdict(float)
    for tree in trees:
        sims = [(c, _similarity(tree.approach, c)) for c in candidate_approaches]
        sims.sort(key=lambda x: -x[1])
        for rank, (candidate, _) in enumerate(sims):
            borda = (n - rank) * tree.weight * max(0.0, tree.outcome)
            scores[candidate] += borda

    total = sum(scores.values())
    if total > 0:
        for c in scores:
            scores[c] /= total

    return dict(sorted(scores.items(), key=lambda x: -x[1]))
