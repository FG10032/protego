import json
from pathlib import Path

import pytest

from builders import PRICING, make_job, make_policy, make_usage
from evaluate import estimate_monthly_cost, evaluate_job
from pipeline_review.__main__ import main

EXAMPLES = Path(__file__).resolve().parent.parent.joinpath("examples")


def test_cost_basic():
    assert estimate_monthly_cost(
        make_job(workers=20), make_usage(runtime=150), PRICING
    ) == pytest.approx(0.768 * 20 * 150)


@pytest.mark.parametrize("job, usage", [
    (make_job(instance_type="a1b.2xlarge"), make_usage()),
    (make_job(), make_usage(runtime=None)),
])
def test_cost_is_none_without_basis(job, usage):
    assert estimate_monthly_cost(job, usage, PRICING) is None


def test_clean_job_passes():
    job = make_job(instance_type="m7g.4xlarge", architecture="arm64", workers=4)
    result = evaluate_job(job, make_policy(), {job.name: make_usage(avg_cpu=0.5, p95_cpu=0.6, avg_mem=0.6)})
    assert result.status == "pass"
    assert result.messages == []


def test_warn_status_when_only_warnings():
    job = make_job(architecture="x86_64", workers=4)
    result = evaluate_job(job, make_policy(), {job.name: make_usage(avg_cpu=0.5, p95_cpu=0.6, avg_mem=0.6)})
    assert result.status == "warn"


def test_sample_clickstream_end_to_end():
    job = make_job(name="clickstream-daily-rollup", instance_type="m6i.4xlarge", workers=20,
                   architecture="x86_64", executor_cores=4, executor_memory_gb=16, dynamic_allocation=False)
    result = evaluate_job(job, make_policy(), {"clickstream-daily-rollup": make_usage(0.28, 0.46, 0.42, 150)})
    codes = {m.code for m in result.messages}
    assert result.status == "fail"
    assert {"DYNAMIC_ALLOCATION_REQUIRED", "RIGHTSIZE_AVAILABLE"} <= codes
    assert result.estimated_monthly_cost == pytest.approx(2304.0)
    assert result.potential_monthly_savings == pytest.approx(576.0)


def test_cli_runs_on_examples_and_gates(capsys):
    code = main([
        str(EXAMPLES.joinpath("jobs.yaml")),
        str(EXAMPLES.joinpath("policy.yaml")),
        "--usage",
        str(EXAMPLES.joinpath("usage.json")),
    ])
    data = json.loads(capsys.readouterr().out)
    assert code == 1
    assert [r["name"] for r in data["results"]] == ["clickstream-daily-rollup", "ads-events-stream"]
