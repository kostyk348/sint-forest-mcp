import random
from pathlib import Path
from typing import Optional

from config import DATA_DIR
from forest.trees import ExperienceTree, ForestStore


def sample_from_domain(domain: str, k: int) -> list[ExperienceTree]:
    store = ForestStore(domain)
    trees = store.all()
    if not trees:
        return []
    weights = [t.weight for t in trees]
    total = sum(weights)
    if total == 0:
        return random.sample(trees, min(k, len(trees)))
    probs = [w / total for w in weights]
    return list(random.choices(trees, weights=probs, k=min(k, len(trees))))


def get_related_domains(domain: str, max_related: int = 3) -> list[str]:
    base = Path(DATA_DIR).expanduser()
    if not base.exists():
        return []
    all_domains = [f.stem for f in base.iterdir() if f.suffix == ".json"]
    return [d for d in all_domains if d != domain][:max_related]


def forest_sample(domain: str, k: int, m: int = 2) -> list[dict]:
    primary = sample_from_domain(domain, k)
    related_domains = get_related_domains(domain)
    extra = []
    for rd in related_domains[:m]:
        extra.extend(sample_from_domain(rd, max(1, k // 2)))
    result = primary + extra
    random.shuffle(result)
    return [t.to_dict() for t in result]
