import argparse
import json
import sys
from pathlib import Path

from evaluate import evaluate_job
from loaders.load_job import load_jobs
from loaders.load_policy import load_policy
from loaders.load_usage import load_usage
from models import JobResult


def _round(value):
    return round(value, 2) if value is not None else None


def _result_to_dict(result: JobResult) -> dict:
    return {
        "name": result.name,
        "env": result.env,
        "status": result.status,
        "estimated_monthly_cost": _round(result.estimated_monthly_cost),
        "potential_monthly_savings": _round(result.potential_monthly_savings),
        "messages": [
            {
                "code": m.code,
                "level": m.level.value,
                "cause": m.cause,
                "suggestion": m.suggestion,
            }
            for m in result.messages
        ],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="pipeline_review",
        description="Review pipeline job configs against policy and usage, emit a JSON report.",
    )
    parser.add_argument("jobs", help="path to jobs YAML")
    parser.add_argument("policy", help="path to policy YAML")
    parser.add_argument("--usage", help="path to usage JSON (optional)")
    parser.add_argument("--out", help="write report to this path (default: stdout)")
    args = parser.parse_args(argv)

    try:
        jobs = load_jobs(Path(args.jobs))
        policy = load_policy(Path(args.policy))
        usages = load_usage(Path(args.usage)) if args.usage else {}
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    results = [evaluate_job(job, policy, usages) for job in jobs]
    report = {"results": [_result_to_dict(r) for r in results]}
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"

    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
        print(f"wrote report to {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(payload)

    if any(r.status == "fail" for r in results):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
