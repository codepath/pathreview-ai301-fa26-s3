"""Run the RAG evaluation suite against benchmark portfolios."""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

# Allow `python scripts/run_evals.py` from the repo root (make eval, CI).
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from rag.evaluator.eval_suite import EvalSuite  # noqa: E402

DEFAULT_PROFILES_DIR = REPO_ROOT / "tests" / "fixtures" / "sample_profiles"
DEFAULT_OUTPUT = REPO_ROOT / "eval_results.json"


def load_profiles(profiles_dir: Path) -> list[tuple[str, dict]]:
    """Load every benchmark profile (*.json) in a directory, sorted by file name."""
    return [
        (path.stem, json.loads(path.read_text(encoding="utf-8")))
        for path in sorted(profiles_dir.glob("*.json"))
    ]


def build_case(profile: dict) -> tuple[str, list[dict], str]:
    """Turn a profile into an offline (query, chunks, feedback) case.

    Chunks are the profile's repo descriptions and READMEs, the query is built
    from the repo languages and topics, and the feedback is a deterministic
    stand-in for LLM output, so no network or model call is needed.
    """
    repos = profile.get("repos", [])
    terms = []
    for repo in repos:
        terms.append(repo.get("language") or "")
        terms.extend(repo.get("topics", []))
    query = " ".join(term for term in terms if term)

    chunks = [
        {"text": f"{repo.get('description') or ''} {repo.get('readme_content') or ''}".strip()}
        for repo in repos
    ]

    feedback = ". ".join(
        f"{repo['name']} is a {repo.get('language') or 'software'} project: "
        f"{repo.get('description') or ''}"
        for repo in repos
    )
    return query, chunks, feedback


def run(profiles_dir: Path, output: Path) -> dict:
    """Score every profile with EvalSuite and write the report to `output`."""
    suite = EvalSuite()
    results = []
    for name, profile in load_profiles(profiles_dir):
        query, chunks, feedback = build_case(profile)
        scores = suite.run(query, chunks, feedback)
        results.append(
            {
                "profile": name,
                "repo_count": len(chunks),
                "relevance_score": scores.relevance_score,
                "faithfulness_score": scores.faithfulness_score,
                "overall_score": scores.overall_score,
            }
        )

    count = len(results)
    report = {
        "timestamp": datetime.now(UTC).isoformat(),
        "profile_count": count,
        "mean_relevance": sum(r["relevance_score"] for r in results) / count if count else 0.0,
        "mean_faithfulness": (
            sum(r["faithfulness_score"] for r in results) / count if count else 0.0
        ),
        "mean_overall": sum(r["overall_score"] for r in results) / count if count else 0.0,
        "results": results,
    }
    if count:
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    """Execute the full evaluation pipeline and output results."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profiles-dir", type=Path, default=DEFAULT_PROFILES_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    print("Running RAG evaluation suite...")
    report = run(args.profiles_dir, args.output)
    if report["profile_count"] == 0:
        print(f"No benchmark profiles found in {args.profiles_dir}", file=sys.stderr)
        return 1
    print(f"Scored {report['profile_count']} profile(s), mean overall {report['mean_overall']:.3f}")
    print(f"Evaluation complete. Results written to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
