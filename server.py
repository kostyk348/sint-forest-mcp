import time

from fastmcp import FastMCP

from config import NAME, VERSION
from forest.forgetting import forest_forget, forest_consolidate
from forest.sampling import forest_sample
from forest.trees import ExperienceTree, ForestStore
from forest.voting import forest_vote

mcp = FastMCP(NAME, version=VERSION)


@mcp.tool()
def forest_seed(domain: str) -> str:
    store = ForestStore(domain)
    store.clear()
    return f"Forest seeded for domain '{domain}'. Ready for learning."


@mcp.tool()
def forest_learn(
    domain: str,
    problem: str,
    approach: str,
    outcome: float,
    weight: float = 1.0,
    tags: list[str] = None,
) -> str:
    tree = ExperienceTree(
        domain=domain,
        problem=problem,
        approach=approach,
        outcome=outcome,
        weight=weight,
        tags=tags or [],
    )
    store = ForestStore(domain)
    store.add(tree)
    return f"Learned experience tree {tree.id} in domain '{domain}' (weight={weight}, outcome={outcome})"


@mcp.tool()
def forest_sample_trees(domain: str, k: int = 5) -> list[dict]:
    return forest_sample(domain, k=k, m=2)


@mcp.tool()
def forest_vote_on_approaches(
    domain: str, problem: str, candidate_approaches: list[str]
) -> dict[str, float]:
    return forest_vote(domain, problem, candidate_approaches)


@mcp.tool()
def forest_forget_weak(domain: str, threshold: float = 0.1) -> str:
    removed = forest_forget(domain, threshold)
    return f"Removed {removed} trees below threshold {threshold} in domain '{domain}'"


@mcp.tool()
def forest_consolidate_similar(domain: str, similarity_threshold: float = 0.7) -> str:
    merged = forest_consolidate(domain, similarity_threshold)
    return f"Merged {merged} similar trees in domain '{domain}' (threshold={similarity_threshold})"


@mcp.tool()
def forest_stats(domain: str) -> dict:
    store = ForestStore(domain)
    trees = store.all()
    if not trees:
        return {"domain": domain, "trees": 0}

    total_weight = sum(t.weight for t in trees)
    avg_outcome = sum(t.outcome for t in trees) / len(trees)
    contradiction_total = sum(t.contradiction_count for t in trees)
    approaches = {}
    for t in trees:
        first_word = t.approach.split()[0] if t.approach.split() else "unknown"
        approaches[first_word] = approaches.get(first_word, 0) + 1
    top_approaches = sorted(approaches.items(), key=lambda x: -x[1])[:5]

    age_days = (time.time() - min(t.timestamp for t in trees)) / 86400.0

    return {
        "domain": domain,
        "trees": len(trees),
        "total_weight": round(total_weight, 2),
        "avg_outcome": round(avg_outcome, 3),
        "total_contradictions": contradiction_total,
        "forest_age_days": round(age_days, 1),
        "unique_tags": len(set(t for tree in trees for t in tree.tags)),
        "top_approach_prefixes": dict(top_approaches),
    }


if __name__ == "__main__":
    mcp.run()
