import hashlib
import json
import time
from pathlib import Path
from typing import Optional

from config import DATA_DIR


class ExperienceTree:
    def __init__(
        self,
        domain: str,
        problem: str,
        approach: str,
        outcome: float,
        weight: float = 1.0,
        tags: Optional[list[str]] = None,
        tree_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        contradiction_count: int = 0,
    ):
        self.domain = domain
        self.problem = problem
        self.problem_hash = hashlib.sha256(problem.encode()).hexdigest()[:16]
        self.approach = approach
        self.outcome = outcome
        self.weight = weight
        self.tags = tags or []
        self.timestamp = timestamp or time.time()
        self.contradiction_count = contradiction_count
        self.id = tree_id or self._generate_id()

    def _generate_id(self) -> str:
        raw = f"{self.domain}|{self.problem_hash}|{self.approach}|{self.timestamp}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "domain": self.domain,
            "problem_hash": self.problem_hash,
            "approach": self.approach,
            "outcome": self.outcome,
            "weight": self.weight,
            "timestamp": self.timestamp,
            "tags": self.tags,
            "contradiction_count": self.contradiction_count,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ExperienceTree":
        return cls(
            domain=d["domain"],
            problem=d.get("problem", ""),
            approach=d["approach"],
            outcome=d["outcome"],
            weight=d["weight"],
            tags=d.get("tags", []),
            tree_id=d["id"],
            timestamp=d["timestamp"],
            contradiction_count=d.get("contradiction_count", 0),
        )


class ForestStore:
    def __init__(self, domain: str):
        self.domain = domain
        base = Path(DATA_DIR).expanduser()
        base.mkdir(parents=True, exist_ok=True)
        self.path = base / f"{domain}.json"
        self.trees: list[ExperienceTree] = []
        self._load()

    def _load(self):
        if self.path.exists():
            with open(self.path) as f:
                data = json.load(f)
            self.trees = [ExperienceTree.from_dict(t) for t in data.get("trees", [])]

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            json.dump({"domain": self.domain, "trees": [t.to_dict() for t in self.trees]}, f, indent=2)

    def add(self, tree: ExperienceTree):
        self.trees.append(tree)
        self._save()

    def all(self) -> list[ExperienceTree]:
        return list(self.trees)

    def clear(self):
        self.trees = []
        self._save()

    def replace_all(self, trees: list[ExperienceTree]):
        self.trees = list(trees)
        self._save()
