from dataclasses import replace

import pytest
from builders import PRICING, QA_POLICY, make_job, make_usage
from guardrails.rightsizing import rightsize


def _cost(workers, hourly, runtime):
    return workers * hourly * runtime


def test_rightsize_reduces_workers_and_computes_savings():
    job = make_job(instance_type="m6i.4xlarge", workers=20)
    usage = make_usage(p95_cpu=0.46, avg_mem=0.42, runtime=150)
    msg, savings = rightsize(job, QA_POLICY, usage, PRICING, _cost(20, 0.768, 150))
    assert msg.code == "RIGHTSIZE_AVAILABLE"
    assert savings == pytest.approx(0.768 * 5 * 150)
    assert "20 to 15" in msg.suggestion


def test_rightsize_boundary_projected_lands_on_target():
    job = make_job(workers=20)
    usage = make_usage(p95_cpu=0.325, avg_mem=0.10, runtime=150)
    msg, _ = rightsize(job, QA_POLICY, usage, PRICING, _cost(20, 0.768, 150))
    assert "20 to 10" in msg.suggestion


def test_rightsize_conflicting_signals_no_recommendation():
    job = make_job(workers=20)
    usage = make_usage(p95_cpu=0.20, avg_mem=0.62, runtime=150)
    assert rightsize(job, QA_POLICY, usage, PRICING, _cost(20, 0.768, 150)) == (None, None)


def test_rightsize_hot_p95_no_shrink():
    job = make_job(instance_type="m6i.2xlarge", workers=8)
    usage = make_usage(p95_cpu=0.78, avg_mem=0.55, runtime=730)
    msg, savings = rightsize(job, QA_POLICY, usage, PRICING, _cost(8, 0.384, 730))
    assert (msg, savings) == (None, None)


@pytest.mark.parametrize("job, policy, usage, cost", [
    (make_job(), QA_POLICY, None, 100.0),
    (make_job(), replace(QA_POLICY, target_utilization=None), make_usage(), 100.0),
    (make_job(), QA_POLICY, make_usage(p95_cpu=None), 100.0),
])
def test_rightsize_skips_without_enough_data(job, policy, usage, cost):
    assert rightsize(job, policy, usage, PRICING, cost) == (None, None)
