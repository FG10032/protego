# protego

Python tool reviewing spark job configurations and produce report

## Requirements

Required Python version is 3.10+.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Usage

```bash
.venv/bin/python -m pipeline_review examples/jobs.yaml examples/policy.yaml \
    --usage examples/usage.json \
    --out examples/report.json
```

replace `examples/*.yaml`, `examples/*.json` with work file path

- `--usage`: optional. If empty, jobs will be evaluated with `MISSING_USAGE_DATA`. Cost estimation and rightsizing will
  be skipped.
- `--out`: optional. If empty, the report prints to stdout.

## Output

```json
{
  "results": [
    {
      "env": "prod",
      "estimated_monthly_cost": 2304.0,
      "messages": [
        {
          "cause": "Batch job has dynamic allocation disabled but policy requires it.",
          "code": "DYNAMIC_ALLOCATION_REQUIRED",
          "level": "error",
          "suggestion": "Set spark.dynamic_allocation to true for batch job."
        },
        "..."
      ],
      "name": "clickstream-daily-rollup",
      "potential_monthly_savings": 576.0,
      "status": "fail"
    },
    "..."
  ]
}
```

## Tests

```bash
.venv/bin/python -m pytest
```
